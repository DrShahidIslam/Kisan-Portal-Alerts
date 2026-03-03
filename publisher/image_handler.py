"""
Image Handler — Generates AI featured images via Gemini Imagen
and compresses them to WebP under 100KB for SEO + hosting efficiency.
"""
import logging
import io
import os
import re
from datetime import datetime

from PIL import Image
from google import genai

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config
from writer.seo_prompt import build_image_prompt
from gemini_client import generate_content_with_fallback, generate_image_with_fallback, generate_image_with_gemini_flash

logger = logging.getLogger(__name__)

# Max file size in bytes (100KB)
MAX_FILE_SIZE = 100 * 1024
# Target dimensions (1200x630 is standard OG/featured image)
TARGET_WIDTH = 1200
TARGET_HEIGHT = 630


def _compress_to_webp(image_path_or_bytes, output_path, max_size=MAX_FILE_SIZE):
    """
    Compress an image to WebP format under the target file size.
    Applies resizing to 1200x630 and iteratively reduces quality until under limit.

    Args:
        image_path_or_bytes: Path to source image or raw bytes
        output_path: Where to save the compressed WebP
        max_size: Maximum file size in bytes (default 100KB)

    Returns:
        str: Path to the compressed WebP file, or None if failed
    """
    try:
        # Open the image
        if isinstance(image_path_or_bytes, Image.Image):
            img = image_path_or_bytes
        elif isinstance(image_path_or_bytes, bytes):
            img = Image.open(io.BytesIO(image_path_or_bytes))
        else:
            img = Image.open(image_path_or_bytes)

        # Convert to RGB if necessary (RGBA/palette modes don't work well with WebP lossy)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        # Resize to target dimensions (1200x630) maintaining aspect ratio then cropping
        img = _resize_and_crop(img, TARGET_WIDTH, TARGET_HEIGHT)

        # Ensure output path has .webp extension
        if not output_path.lower().endswith(".webp"):
            output_path = os.path.splitext(output_path)[0] + ".webp"

        # Iteratively compress until under max_size
        quality = 85  # Start at high quality
        while quality >= 10:
            buffer = io.BytesIO()
            img.save(buffer, format="WEBP", quality=quality, method=6)
            size = buffer.tell()

            if size <= max_size:
                # Write to file
                with open(output_path, "wb") as f:
                    f.write(buffer.getvalue())

                final_kb = size / 1024
                logger.info(f"    Compressed to WebP: {final_kb:.1f}KB (quality={quality})")
                return output_path

            # Reduce quality and try again
            quality -= 5

        # Last resort: aggressive resize + minimum quality
        img = img.resize((800, 420), Image.LANCZOS)
        buffer = io.BytesIO()
        img.save(buffer, format="WEBP", quality=10, method=6)
        with open(output_path, "wb") as f:
            f.write(buffer.getvalue())

        final_kb = buffer.tell() / 1024
        logger.info(f"    Compressed to WebP (aggressive): {final_kb:.1f}KB")
        return output_path

    except Exception as e:
        logger.error(f"    WebP compression error: {e}")
        return None

def _compress_to_jpg(image_path_or_bytes, output_path, max_size=MAX_FILE_SIZE):
    """
    Compress an image to JPEG format under the target file size.
    Applies resizing to 1200x630 and iteratively reduces quality until under limit.
    """
    try:
        if isinstance(image_path_or_bytes, Image.Image):
            img = image_path_or_bytes
        elif isinstance(image_path_or_bytes, bytes):
            img = Image.open(io.BytesIO(image_path_or_bytes))
        else:
            img = Image.open(image_path_or_bytes)

        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        img = _resize_and_crop(img, TARGET_WIDTH, TARGET_HEIGHT)

        if not output_path.lower().endswith((".jpg", ".jpeg")):
            output_path = os.path.splitext(output_path)[0] + ".jpg"

        quality = 85
        while quality >= 10:
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=quality, optimize=True)
            size = buffer.tell()

            if size <= max_size:
                with open(output_path, "wb") as f:
                    f.write(buffer.getvalue())
                return output_path
            quality -= 5

        img = img.resize((800, 420), Image.LANCZOS)
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=15, optimize=True)
        with open(output_path, "wb") as f:
            f.write(buffer.getvalue())
        return output_path

    except Exception as e:
        logger.error(f"    JPEG compression error: {e}")
        return None


def _resize_and_crop(img, target_w, target_h):
    """Resize image to fill target dimensions, then center-crop."""
    # Calculate scale to fill
    w_ratio = target_w / img.width
    h_ratio = target_h / img.height
    scale = max(w_ratio, h_ratio)

    new_w = int(img.width * scale)
    new_h = int(img.height * scale)
    img = img.resize((new_w, new_h), Image.LANCZOS)

    # Center crop
    left = (new_w - target_w) // 2
    top = (new_h - target_h) // 2
    img = img.crop((left, top, left + target_w, top + target_h))

    return img


def _try_gemini_flash_image(article_title, output_path_webp, output_path_jpg):
    """Try Gemini 2.5 Flash Image (free tier). Returns (webp, jpg) or (None, None)."""
    try:
        prompt = build_image_prompt(article_title)
        response = generate_image_with_gemini_flash(prompt)
        if not response or not getattr(response, "candidates", None):
            return None, None
        for part in response.candidates[0].content.parts:
            if getattr(part, "inline_data", None) and getattr(part.inline_data, "data", None):
                image_bytes = part.inline_data.data
                if isinstance(image_bytes, bytes) and len(image_bytes) > 100:
                    result_webp = _compress_to_webp(image_bytes, output_path_webp)
                    result_jpg = _compress_to_jpg(image_bytes, output_path_jpg)
                    if result_webp and result_jpg:
                        logger.info(f"    Images ready from Gemini Flash Image: {result_webp}, {result_jpg}")
                        return result_webp, result_jpg
                break
    except Exception as e:
        logger.warning(f"    Gemini Flash Image failed: {e}")
    return None, None


def _try_source_image(source_url, output_path_webp, output_path_jpg):
    """Try to use the featured image from the source article (og:image or first large img). Returns (webp, jpg) or (None, None)."""
    if not source_url or not source_url.startswith("http") or "trends.google" in source_url:
        return None, None
    try:
        import requests
        from urllib.parse import urljoin
        headers = {"User-Agent": "Mozilla/5.0 (compatible; KisanPortalAgent/1.0; +https://kisanportal.org)"}
        r = requests.get(source_url, headers=headers, timeout=12)
        r.raise_for_status()
        html = r.text
        image_url = None
        m = re.search(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']', html, re.I)
        if m:
            image_url = m.group(1).strip()
        if not image_url:
            m = re.search(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']', html, re.I)
            if m:
                image_url = m.group(1).strip()
        if not image_url:
            for m in re.finditer(r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>', html, re.I):
                src = m.group(1).strip()
                if "logo" in src.lower() or "avatar" in src.lower() or "icon" in src.lower():
                    continue
                image_url = src
                break
        if not image_url:
            return None, None
        image_url = urljoin(source_url, image_url)
        img_r = requests.get(image_url, headers=headers, timeout=12)
        img_r.raise_for_status()
        image_bytes = img_r.content
        if len(image_bytes) < 3000:
            return None, None
        result_webp = _compress_to_webp(image_bytes, output_path_webp)
        result_jpg = _compress_to_jpg(image_bytes, output_path_jpg)
        if result_webp and result_jpg:
            logger.info(f"    Image from source article (fallback when generation failed): {result_webp}, {result_jpg}")
            return result_webp, result_jpg
    except Exception as e:
        logger.warning(f"    Source image failed: {e}")
    return None, None


def _try_unsplash_image(article_title, output_path_webp, output_path_jpg):
    """Try Unsplash API for a high-quality stock photo (optional; needs UNSPLASH_ACCESS_KEY). Returns (webp, jpg) or (None, None)."""
    key = getattr(config, "UNSPLASH_ACCESS_KEY", None)
    if not key:
        return None, None
    try:
        import requests
        # Build search query: prefer agriculture/farm terms; fallback to first few words of title
        q = re.sub(r"[^a-zA-Z0-9\s]", "", article_title)[:40].strip()
        if not q or len(q.split()) < 2:
            q = "indian agriculture farm"
        # Unsplash search
        r = requests.get(
            "https://api.unsplash.com/search/photos",
            params={"query": q, "client_id": key, "per_page": 1, "orientation": "landscape"},
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()
        results = data.get("results") or []
        if not results:
            return None, None
        url = results[0].get("urls", {}).get("regular") or results[0].get("urls", {}).get("small")
        if not url:
            return None, None
        img_r = requests.get(url, timeout=15)
        img_r.raise_for_status()
        image_bytes = img_r.content
        if len(image_bytes) < 5000:
            return None, None
        result_webp = _compress_to_webp(image_bytes, output_path_webp)
        result_jpg = _compress_to_jpg(image_bytes, output_path_jpg)
        if result_webp and result_jpg:
            logger.info(f"    Image from Unsplash: {result_webp}, {result_jpg}")
            return result_webp, result_jpg
    except Exception as e:
        logger.warning(f"    Unsplash failed: {e}")
    return None, None


def _try_pollinations_image(article_title, output_path_webp, output_path_jpg):
    """Try Pollinations.ai (free). Returns (webp, jpg) or (None, None)."""
    return _generate_pollinations_image(article_title, output_path_webp, output_path_jpg)


def _generate_placeholder_image(article_title, output_path_webp, output_path_jpg):
    """Generate a simple placeholder image (solid color + title text)."""
    from PIL import ImageDraw, ImageFont
    try:
        width, height = TARGET_WIDTH, TARGET_HEIGHT
        img = Image.new("RGB", (width, height), color=(20, 80, 40))  # Agri green
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 42)
        except OSError:
            try:
                font = ImageFont.truetype("arial.ttf", 42)
            except OSError:
                font = ImageFont.load_default()
        words = article_title.split()
        lines, current_line = [], ""
        for word in words:
            test_line = f"{current_line} {word}".strip()
            if len(test_line) > 35:
                if current_line:
                    lines.append(current_line)
                current_line = word
            else:
                current_line = test_line
        if current_line:
            lines.append(current_line)
        y_pos = height // 2 - len(lines) * 30
        for line in lines[:4]:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            draw.text(((width - text_width) // 2, y_pos), line, fill=(255, 255, 255), font=font)
            y_pos += 55
        result_webp = _compress_to_webp(img, output_path_webp)
        result_jpg = _compress_to_jpg(img, output_path_jpg)
        return result_webp, result_jpg
    except Exception as e:
        logger.error(f"    Placeholder image error: {e}")
        return None, None


def generate_featured_image(article_title, save_dir=None, source_url=None):
    """
    Generate a featured image. Order (same as FIFA alerts app):
    1. Gemini Flash Image (free)
    2. Source article image (og:image or first img) — used when image generation fails; no quota cost
    3. Pollinations (free)
    4. Imagen (if USE_GEMINI_IMAGEN)
    5. Placeholder (title text on solid color)
    Compresses to WebP and JPEG under 100KB.
    """
    if save_dir is None:
        save_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "images")
    os.makedirs(save_dir, exist_ok=True)

    slug = re.sub(r"[^a-z0-9]+", "-", article_title.lower())[:50].strip("-")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path_webp = os.path.join(save_dir, f"{slug}_{timestamp}.webp")
    output_path_jpg = os.path.join(save_dir, f"{slug}_{timestamp}.jpg")

    logger.info(f"  Generating featured image for: {article_title[:60]}")

    # 0. Optional: Unsplash (high-quality real photos when key is set)
    if getattr(config, "UNSPLASH_ACCESS_KEY", None):
        webp, jpg = _try_unsplash_image(article_title, output_path_webp, output_path_jpg)
        if webp and jpg:
            return webp, jpg

    # 1. Free tier: Gemini 2.5 Flash Image
    webp, jpg = _try_gemini_flash_image(article_title, output_path_webp, output_path_jpg)
    if webp and jpg:
        return webp, jpg

    # 2. When image generation fails: use image from source article (og:image or first img) — same as FIFA
    if source_url:
        webp, jpg = _try_source_image(source_url, output_path_webp, output_path_jpg)
        if webp and jpg:
            return webp, jpg

    # 3. Free: Pollinations
    webp, jpg = _try_pollinations_image(article_title, output_path_webp, output_path_jpg)
    if webp and jpg:
        return webp, jpg

    # 4. Paid tier only: Imagen (skip on free tier to avoid 400 errors)
    if getattr(config, "USE_GEMINI_IMAGEN", False):
        try:
            prompt = build_image_prompt(article_title)
            generation_config = genai.types.GenerateImagesConfig(
                number_of_images=1,
                output_mime_type="image/jpeg",
                aspect_ratio="16:9",
            )
            response = generate_image_with_fallback(
                model=getattr(config, "IMAGEN_MODEL", "imagen-3.0-generate-002"),
                prompt=prompt,
                generation_config=generation_config,
            )
            if response.generated_images:
                for generated_image in response.generated_images:
                    result_webp = _compress_to_webp(generated_image.image.image_bytes, output_path_webp)
                    result_jpg = _compress_to_jpg(generated_image.image.image_bytes, output_path_jpg)
                    if result_webp and result_jpg:
                        logger.info(f"    Images ready from Imagen: {result_webp}, {result_jpg}")
                        return result_webp, result_jpg
        except Exception as e:
            logger.warning(f"    Imagen failed: {e}")

    # 5. Placeholder disabled by default (user prefers no image over plain green)
    if getattr(config, "USE_PLACEHOLDER_IMAGE", False):
        logger.info("    Using placeholder image (title text)")
        return _generate_placeholder_image(article_title, output_path_webp, output_path_jpg)
    logger.warning("    No image generated (all sources failed). Post will publish without featured image.")
    return None, None


def _generate_pollinations_image(article_title, output_path_webp, output_path_jpg):
    """
    Create a beautiful AI image using pollinations.ai (Flux model).
    Outputs as compressed WebP and JPEG under 100KB.
    """
    import urllib.request
    import urllib.parse
    import time
    from PIL import Image, ImageDraw
    import io

    try:
        logger.info(f"    Fetching high-quality image from Pollinations (Flux)...")
        
        # Build prompt: clear, editorial, no text (better AI image quality)
        prompt = f"Professional editorial photograph, Indian agriculture, farm or crop field, natural daylight, photorealistic, high quality, for article: {article_title}. No text, no logos, no watermark, landscape."
        safe_prompt = urllib.parse.quote(prompt)
        
        # Use FLUX model on Pollinations for premium quality
        seed = int(time.time() * 1000) % 1000000
        url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width={TARGET_WIDTH}&height={TARGET_HEIGHT}&seed={seed}&nologo=true&model=flux"
        
        # Download with timeout and user-agent
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=45) as response:
            image_bytes = response.read()
            
        if not image_bytes or len(image_bytes) < 1000:
            raise Exception("Received empty or invalid image from Pollinations")

        result_webp = _compress_to_webp(image_bytes, output_path_webp)
        result_jpg = _compress_to_jpg(image_bytes, output_path_jpg)
        
        if result_webp and result_jpg:
             logger.info("    ✅ Image generated successfully via Pollinations (Flux)")
             return result_webp, result_jpg
        
        raise Exception("Pollinations compression failed")

    except Exception as e:
        logger.warning(f"    Pollinations error: {e}. Falling back to gradient.")
        return _generate_gradient_fallback(output_path_webp, output_path_jpg)


def _generate_gradient_fallback(output_path_webp, output_path_jpg):
    """Absolute final resort: Beautiful abstract gradient."""
    try:
        from PIL import Image, ImageDraw
        width, height = TARGET_WIDTH, TARGET_HEIGHT
        # Create a simple vertical gradient (Forest Green to Lime Green)
        img = Image.new('RGB', (width, height), color=(34, 139, 34))
        draw = ImageDraw.Draw(img)
        
        for i in range(height):
            # Gradient from (34, 139, 34) to (50, 205, 50)
            r = 34 + int((50 - 34) * i / height)
            g = 139 + int((205 - 139) * i / height)
            b = 34 + int((50 - 34) * i / height)
            draw.line([(0, i), (width, i)], fill=(r, g, b))
        
        result_webp = _compress_to_webp(img, output_path_webp)
        result_jpg = _compress_to_jpg(img, output_path_jpg)
        logger.info("    ⚠️ Using gradient fallback as absolute last resort")
        return result_webp, result_jpg

    except Exception as fallback_e:
        logger.error(f"    Hard fallback error: {fallback_e}")
        return None, None


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test_title = "PM-Kisan 19th Installment Date Announced for 2026"
    webp_path, jpg_path = generate_featured_image(test_title)
    if webp_path and jpg_path:
        size_kb = os.path.getsize(webp_path) / 1024
        print(f"Image: {webp_path} ({size_kb:.1f}KB)")
    else:
        print("Image generation failed")
