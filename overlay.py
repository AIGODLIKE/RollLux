"""Floating reference image drawn directly in the 3D viewport.

Unlike a camera background image, this is a screen-space overlay anchored to a
corner of the viewport, with adjustable size and opacity. Implemented with a
``SpaceView3D`` POST_PIXEL draw handler.
"""

from __future__ import annotations

import bpy

try:
    import gpu
    from gpu_extras.batch import batch_for_shader
    _GPU_OK = True
except Exception:  # headless builds without the gpu module
    _GPU_OK = False

_handle = None
_MARGIN = 16


def _get_shader():
    # 'IMAGE_COLOR' lets us multiply by a color (for opacity); fall back to 'IMAGE'.
    try:
        return gpu.shader.from_builtin("IMAGE_COLOR"), True
    except Exception:
        return gpu.shader.from_builtin("IMAGE"), False


def _draw():
    context = bpy.context
    scene = getattr(context, "scene", None)
    if scene is None:
        return
    s = scene.rolllux
    if not s.float_show or s.reference_image is None:
        return

    img = s.reference_image
    iw, ih = img.size
    if iw == 0 or ih == 0:
        return

    region = context.region
    if region is None:
        return
    rw, rh = region.width, region.height

    # Width is a fraction of the viewport; height keeps the image aspect.
    width = rw * 0.32 * s.float_scale
    height = width * (ih / iw)
    height = min(height, rh * 0.7)
    width = height * (iw / ih)

    if "LEFT" in s.float_corner:
        x0 = _MARGIN
    else:
        x0 = rw - width - _MARGIN
    if "TOP" in s.float_corner:
        y0 = rh - height - _MARGIN
    else:
        y0 = _MARGIN
    x1, y1 = x0 + width, y0 + height

    try:
        texture = gpu.texture.from_image(img)
    except Exception:
        return

    shader, has_color = _get_shader()
    batch = batch_for_shader(
        shader, "TRI_FAN",
        {
            "pos": ((x0, y0), (x1, y0), (x1, y1), (x0, y1)),
            "texCoord": ((0, 0), (1, 0), (1, 1), (0, 1)),
        },
    )

    gpu.state.blend_set("ALPHA")
    shader.bind()
    shader.uniform_sampler("image", texture)
    if has_color:
        shader.uniform_float("color", (1.0, 1.0, 1.0, s.float_opacity))
    batch.draw(shader)

    # Thin frame around it.
    try:
        line_shader = gpu.shader.from_builtin("UNIFORM_COLOR")
        frame = batch_for_shader(
            line_shader, "LINE_LOOP",
            {"pos": ((x0, y0), (x1, y0), (x1, y1), (x0, y1))},
        )
        line_shader.bind()
        line_shader.uniform_float("color", (1.0, 1.0, 1.0, 0.35 * s.float_opacity))
        frame.draw(line_shader)
    except Exception:
        pass
    gpu.state.blend_set("NONE")


def tag_redraw():
    wm = bpy.context.window_manager
    if wm is None:
        return
    for win in wm.windows:
        for area in win.screen.areas:
            if area.type == "VIEW_3D":
                area.tag_redraw()


def enable():
    global _handle
    if not _GPU_OK or _handle is not None:
        return
    _handle = bpy.types.SpaceView3D.draw_handler_add(_draw, (), "WINDOW", "POST_PIXEL")
    tag_redraw()


def disable():
    global _handle
    if _handle is not None:
        bpy.types.SpaceView3D.draw_handler_remove(_handle, "WINDOW")
        _handle = None
        tag_redraw()


def on_toggle(self, context):
    if self.float_show:
        enable()
    else:
        disable()


def on_redraw(self, context):
    tag_redraw()


def register():
    pass


def unregister():
    disable()
