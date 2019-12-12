
tree_dot_fmt = """
digraph tree {{
{}
}}
"""


class Tree:
    counter = 0

    def __init__(self, content, children):
        self.content = content
        self.children = children

    def __str__(self):
        return "(" + str(self.content) + " " + " ".join(map(str, self.children)) + ")"

    def terminal_yield(self):
        for c in self.children:
            if isinstance(c, Tree):
                yield from c.terminal_yield()
            else:
                yield c

    def save(self, fname):
        """Saves a dot representation"""
        s = tree_dot_fmt.format("\n".join(self.dot_repr()))
        with open(fname, "w") as f:
            f.write(s)

    save_dot = save

    def dot_repr(self, parent=None):
        lines = []
        ID = Tree.counter
        Tree.counter += 1
        lines.append('    {} [label="{}"]'.format(ID, self.content.replace('"', '\\"')))
        if parent is not None:
            lines.append('    {} -> {}'.format(parent, ID))
        for c in self.children:
            if isinstance(c, Tree):
                lines.extend(c.dot_repr(ID))
            else:
                lines.append('    {} [label="{}", color=red]'.format(Tree.counter, str(c).replace('"', '\\"')))
                lines.append('    {} -> {};'.format(ID, Tree.counter))
                Tree.counter += 1
        return lines

