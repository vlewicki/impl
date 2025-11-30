import dearcygui as dcg


class ModalWindow(dcg.Window):
    def __init__(self, context: dcg.Context, text: str):
        width=400
        height=100
        super().__init__(context, modal=True, no_move=True, no_resize=True, no_title_bar=True, width=width, height=height, x="viewport.width / 2 - self.width / 2", y="viewport.height / 2 - self.height / 2")
        with self:
            with dcg.VerticalLayout(context, alignment_mode=dcg.Alignment.CENTER):
                with dcg.HorizontalLayout(context, alignment_mode=dcg.Alignment.CENTER):
                    dcg.Text(context, value=text)
                with dcg.HorizontalLayout(context, alignment_mode=dcg.Alignment.CENTER):
                        dcg.Button(context, label="OK", callback=self.delete_item)
