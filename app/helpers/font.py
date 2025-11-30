import dearcygui as dcg

def make_font(size, *, main_font_path) -> dcg.GlyphSet:
    font_renderer = dcg.FontRenderer(main_font_path)
    glyphs = font_renderer.render_glyph_set(target_size=size)
    return glyphs
