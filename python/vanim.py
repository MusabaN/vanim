import ast
import os.path

import vim  # type: ignore


class Vanim:
    @property
    def cwd(self):
        return os.path.dirname(vim.current.buffer.name)

    @property
    def file(self):
        return os.path.basename(vim.current.buffer.name)

    @property
    def scene(self):
        cur_line, _ = vim.current.window.cursor
        for node in self._get_scene_nodes():
            if node.lineno <= cur_line <= node.end_lineno:
                return node.name
        return None  # NOTE should this be an error?

    @staticmethod
    def _get_scene_nodes():
        source = "\n".join(vim.current.buffer)  # pack entire buffer into a string lol
        parsed = ast.parse(source)
        for node in ast.walk(parsed):
            if not isinstance(node, ast.ClassDef):
                continue
            # this next test is a bit of a hack but oh well
            if not any("Scene" in base.id for base in node.bases):  # type: ignore
                continue
            yield node

    def render(self, quality, scene=None, preview=True):
        scene = scene or self.scene
        assert scene is not None
        manim_flags = f"{'p' if preview else ''}q{quality}"
        manim_command = f"manim -{manim_flags} {self.file} {scene}"
        # phew! that's a lot of commands!
        vim.command(f"!{manim_command}")

    def render_all(self, quality="h"):
        for node in self._get_scene_nodes():
            self.render(quality, node.name, False)
