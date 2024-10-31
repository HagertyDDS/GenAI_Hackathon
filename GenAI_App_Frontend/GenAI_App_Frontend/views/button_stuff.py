import reflex as rx
from typing import Literal, Callable



LiteralButtonVariant = Literal[
    "primary", "success", "destructive", "secondary", "muted"
]

default_class_name = "font-smbold rounded-xl cursor-pointer inline-flex items-center justify-center px-[0.875rem] py-2 relative transition-bg border-t border-[rgba(255,255,255,0.21)]"

after_class_name = "after:absolute after:inset-[1px] after:border-t after:rounded-[11px] after:border-white after:opacity-[0.22]"


def get_variant_class(variant: str) -> str:
    return (
        f"bg-gradient-to-b from-[--{variant}-9] to-[--{variant}-9] hover:to-[--{variant}-10] text-white"
        + " "
    )


variant_styles = {

    # "primary": {
    #     "class_name": get_variant_class("violet"),
    # },

    "primary": {
        "class_name": get_variant_class("indigo"),
    },

    "success": {
        "class_name": get_variant_class("green"),
    },
    "destructive": {
        "class_name": get_variant_class("red"),
    },
    "muted": {
        "class_name": "bg-slate-3 hover:bg-slate-5 text-slate-9 border-t !border-slate-5",
    },
    "secondary": {
        "class_name": "bg-slate-4 hover:bg-slate-5 text-slate-10 !border-none",
    },
}





#     <!-- HTML !-->
# <button class="button-34" role="button">Button 34</button>

# /* CSS */
# .button-34 {
#   background: #5E5DF0;
#   border-radius: 999px;
#   box-shadow: #5E5DF0 0 10px 20px -10px;
#   box-sizing: border-box;
#   color: #FFFFFF;
#   cursor: pointer;
#   font-family: Inter,Helvetica,"Apple Color Emoji","Segoe UI Emoji",NotoColorEmoji,"Noto Color Emoji","Segoe UI Symbol","Android Emoji",EmojiSymbols,-apple-system,system-ui,"Segoe UI",Roboto,"Helvetica Neue","Noto Sans",sans-serif;
#   font-size: 16px;
#   font-weight: 700;
#   line-height: 24px;
#   opacity: 1;
#   outline: 0 solid transparent;
#   padding: 8px 18px;
#   user-select: none;
#   -webkit-user-select: none;
#   touch-action: manipulation;
#   width: fit-content;
#   word-break: break-word;
#   border: 0;
# }



# button_style = {
#     "background" : "#5E5DF0"
# }

button_style = {
    "background": "#5E5DF0",
    "border_radius": "999px",
    "box_shadow": "#5E5DF0 0 10px 20px -13px",
    "box_sizing": "border-box",
    "color": "#FFFFFF",
    "cursor": "pointer",
    # "font_family": "Inter,Helvetica,'Apple Color Emoji','Segoe UI Emoji',NotoColorEmoji,'Noto Color Emoji','Segoe UI Symbol','Android Emoji',EmojiSymbols,-apple-system,system-ui,'Segoe UI',Roboto,'Helvetica Neue','Noto Sans',sans-serif",
    "font_size": "14px",
    "font_weight": "600",
    "line_height": "24px", 
    "opacity": 1,
    "outline": "0 solid transparent",
    "padding": "8px 18px",
    # "user_select": "none",
    # "touch_action": "manipulation",
    # "width": "fit-content",
    "word_break": "break-word",
    "border": "0",
    "_hover":{
        "opacity": 0.95,
    },
}



button_style_save = {
    "background": "#13aa52",
    "border_radius": "999px",
    "box_shadow": "#24292E 0 10px 20px -15px",
    "box_sizing": "border-box",
    "color": "#FFFFFF",
    "cursor": "pointer",
    # "font_family": "Inter,Helvetica,'Apple Color Emoji','Segoe UI Emoji',NotoColorEmoji,'Noto Color Emoji','Segoe UI Symbol','Android Emoji',EmojiSymbols,-apple-system,system-ui,'Segoe UI',Roboto,'Helvetica Neue','Noto Sans',sans-serif",
    "font_size": "14px",
    "font_weight": "600",
    "line_height": "24px", 
    "opacity": 1,
    "outline": "0 solid transparent",
    "padding": "8px 18px",
    # "user_select": "none",
    # "touch_action": "manipulation",
    # "width": "fit-content",
    "word_break": "break-word",
    "border": "0",
    "_hover":{
        "opacity": 0.95,
    },
}


button_style_remove = {
    "background": "#FF4742",
    "border_radius": "999px",
    "box_shadow": "#5E5DF0 0 10px 20px -15px",
    "box_sizing": "border-box",
    "color": "#FFFFFF",
    "cursor": "pointer",
    # "font_family": "Inter,Helvetica,'Apple Color Emoji','Segoe UI Emoji',NotoColorEmoji,'Noto Color Emoji','Segoe UI Symbol','Android Emoji',EmojiSymbols,-apple-system,system-ui,'Segoe UI',Roboto,'Helvetica Neue','Noto Sans',sans-serif",
    "font_size": "14px",
    "font_weight": "600",
    "line_height": "24px", 
    "opacity": 1,
    "outline": "0 solid transparent",
    "padding": "8px 18px",
    # "user_select": "none",
    # "touch_action": "manipulation",
    # "width": "fit-content",
    "word_break": "break-word",
    "border": "0",
    "_hover":{
        "opacity": 0.95,
    },
}



# border_radius="1em",
                # box_shadow="rgba(128, 128, 128, 0.8) 0 15px 30px -15px",
                # #background_image="linear-gradient(144deg,#AF40FF,#5B42F3 50%,#00DDEB)",
                # box_sizing="border-box",
                # color="white",
                # opacity=1,
                # _hover={
                #     "opacity": 0.5,
                # },



