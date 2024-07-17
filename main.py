import mesop as me
from data_model import State, Models, ModelDialogState, Conversation, ChatMessage
from dialog import dialog, dialog_actions
import claude
import gemini

def change_model_option(e: me.CheckboxChangeEvent):
    s = me.state(ModelDialogState)
    if e.checked:
        s.selected_models.append(e.key)
    else:
        s.selected_models.remove(e.key)

def set_gemini_api_key(e: me.InputBlurEvent):
    me.state(State).gemini_api_key = e.value

def set_claude_api_key(e: me.InputBlurEvent):
    me.state(State).claude_api_key = e.value

def model_picker_dialog():
    state = me.state(State)
    with dialog(state.is_model_picker_dialog_open):
        with me.box(style=me.Style(display="flex", flex_direction="column", gap=12)):
            me.text("API keys")
            me.input(
                label="Gemini API Key",
                value=state.gemini_api_key,
                on_blur=set_gemini_api_key,
            )
            me.input(
                label="Claude API Key",
                value=state.claude_api_key,
                on_blur=set_claude_api_key,
            )
        me.text("Pick a model")
        for model in Models:
            if model.name.startswith("GEMINI"):
                disabled = not state.gemini_api_key
            elif model.name.startswith("CLAUDE"):
                disabled = not state.claude_api_key
            else:
                disabled = False
            me.checkbox(
                key=model.value,
                label=model.value,
                checked=model.value in state.models,
                disabled=disabled,
                on_change=change_model_option,
                style=me.Style(
                    display="flex",
                    flex_direction="column",
                    gap=4,
                    padding=me.Padding(top=12),
                ),
            )
        with dialog_actions():
            me.button("Cancel", on_click=close_model_picker_dialog)
            me.button("Confirm", on_click=confirm_model_picker_dialog)

def close_model_picker_dialog(e: me.ClickEvent):
    state = me.state(State)
    state.is_model_picker_dialog_open = False

def confirm_model_picker_dialog(e: me.ClickEvent):
    dialog_state = me.state(ModelDialogState)
    state = me.state(State)
    state.is_model_picker_dialog_open = False
    state.models = dialog_state.selected_models

ROOT_BOX_STYLE = me.Style(
    background="#e7f2ff",
    height="100%",
    font_family="Inter",
    display="flex",
    flex_direction="column",
)

STYLESHEETS = [
  "https://fonts.googleapis.com/css2?family=Inter:wght@100..900&display=swap"
]

SECURITY_POLICY = me.SecurityPolicy(
    allowed_iframe_parents=["https://huggingface.co"]
)

@me.page(
    path="/",
    stylesheets=STYLESHEETS,
    security_policy=SECURITY_POLICY,
)
def home_page():
    model_picker_dialog()
    with me.box(style=ROOT_BOX_STYLE):
        header()
        with me.box(
            style=me.Style(
                width="min(680px, 100%)",
                margin=me.Margin.symmetric(horizontal="auto", vertical=36),
            )
        ):
            me.text(
                "Chat with multiple models at once",
                style=me.Style(font_size=20, margin=me.Margin(bottom=24)),
            )
            # Uncomment this in the next step:
            examples_row()
            chat_input()

EXAMPLES = [
    "Create a file-lock in Python",
    "Write an email to Congress to have free milk for all",
    "Make a nice box shadow in CSS",
]

def examples_row():
    with me.box(
        style=me.Style(
            display="flex", flex_direction="row", gap=16, margin=me.Margin(bottom=24)
        )
    ):
        for i in EXAMPLES:
            example(i)

def example(text: str):
    with me.box(
        key=text,
        on_click=click_example,
        style=me.Style(
            cursor="pointer",
            background="#b9e1ff",
            width="215px",
            height=160,
            font_weight=500,
            line_height="1.5",
            padding=me.Padding.all(16),
            border_radius=16,
            border=me.Border.all(me.BorderSide(width=1, color="blue", style="none")),
        ),
    ):
        me.text(text)

def click_example(e: me.ClickEvent):
    state = me.state(State)
    state.input = e.key

@me.page(path="/conversation", stylesheets=STYLESHEETS, security_policy=SECURITY_POLICY)
def conversation_page():
    state = me.state(State)
    model_picker_dialog()
    with me.box(style=ROOT_BOX_STYLE):
        header()

        models = len(state.conversations)
        models_px = models * 680
        with me.box(
            style=me.Style(
                width=f"min({models_px}px, calc(100% - 32px))",
                display="grid",
                gap=16,
                grid_template_columns=f"repeat({models}, 1fr)",
                flex_grow=1,
                overflow_y="hidden",
                margin=me.Margin.symmetric(horizontal="auto"),
                padding=me.Padding.symmetric(horizontal=16),
            )
        ):
            for conversation in state.conversations:
                model = conversation.model
                messages = conversation.messages
                with me.box(
                    style=me.Style(
                        overflow_y="auto",
                    )
                ):
                    me.text("Model: " + model, style=me.Style(font_weight=500))

                    for message in messages:
                        if message.role == "user":
                            user_message(message.content)
                        else:
                            model_message(message)
                    if messages and model == state.conversations[-1].model:
                        me.box(
                            key="end_of_messages",
                            style=me.Style(
                                margin=me.Margin(
                                    bottom="50vh" if messages[-1].in_progress else 0
                                )
                            ),
                        )
        with me.box(
            style=me.Style(
                display="flex",
                justify_content="center",
            )
        ):
            with me.box(
                style=me.Style(
                    width="min(680px, 100%)",
                    padding=me.Padding(top=24, bottom=24),
                )
            ):
                chat_input()

def user_message(content: str):
    with me.box(
        style=me.Style(
            background="#e7f2ff",
            padding=me.Padding.all(16),
            margin=me.Margin.symmetric(vertical=16),
            border_radius=16,
        )
    ):
        me.text(content)

def model_message(message: ChatMessage):
    with me.box(
        style=me.Style(
            background="#fff",
            padding=me.Padding.all(16),
            border_radius=16,
            margin=me.Margin.symmetric(vertical=16),
        )
    ):
        me.markdown(message.content)
        if message.in_progress:
            me.progress_spinner()


def header():
    def navigate_home(e: me.ClickEvent):
        me.navigate("/")
        state = me.state(State)
        state.conversations = []

    with me.box(
        on_click=navigate_home,
        style=me.Style(
            cursor="pointer",
            padding=me.Padding.all(16),
        ),
    ):
        me.text(
            "DuoChat",
            style=me.Style(
                font_weight=500,
                font_size=24,
                color="#3D3929",
                letter_spacing="0.3px",
            ),
        )


def switch_model(e: me.ClickEvent):
    state = me.state(State)
    state.is_model_picker_dialog_open = True
    dialog_state = me.state(ModelDialogState)
    dialog_state.selected_models = state.models[:]

def chat_input():
    state = me.state(State)
    with me.box(
        style=me.Style(
            border_radius=16,
            padding=me.Padding.all(8),
            background="white",
            display="flex",
            width="100%",
        )
    ):
        with me.box(style=me.Style(flex_grow=1)):
            me.native_textarea(
                value=state.input,
                placeholder="Enter a prompt",
                on_blur=on_blur,
                style=me.Style(
                    padding=me.Padding(top=16, left=16),
                    outline="none",
                    width="100%",
                    border=me.Border.all(me.BorderSide(style="none")),
                ),
            )
            with me.box(
                style=me.Style(
                    display="flex",
                    padding=me.Padding(left=12, bottom=12),
                    cursor="pointer",
                ),
                on_click=switch_model,
            ):
                me.text(
                    "Model:",
                    style=me.Style(font_weight=500, padding=me.Padding(right=6)),
                )
                if state.models:
                    me.text(", ".join(state.models))
                else:
                    me.text("(no model selected)")
        with me.content_button(
            type="icon", on_click=send_prompt, disabled=not state.models
        ):
            me.icon("send")

def on_blur(e: me.InputBlurEvent):
    state = me.state(State)
    state.input = e.value

def send_prompt(e: me.ClickEvent):
    state = me.state(State)
    if not state.conversations:
        me.navigate("/conversation")
        for model in state.models:
            state.conversations.append(Conversation(model=model, messages=[]))
    input = state.input
    state.input = ""

    for conversation in state.conversations:
        model = conversation.model
        messages = conversation.messages
        history = messages[:]
        messages.append(ChatMessage(role="user", content=input))
        messages.append(ChatMessage(role="model", in_progress=True))
        yield
        me.scroll_into_view(key="end_of_messages")
        if model == Models.GEMINI_1_5_FLASH.value:
            llm_response = gemini.send_prompt_flash(input, history)
        elif model == Models.GEMINI_1_5_PRO.value:
            llm_response = gemini.send_prompt_pro(input, history)
        elif model == Models.CLAUDE_3_5_SONNET.value:
            llm_response = claude.call_claude_sonnet(input, history)
        else:
            raise Exception("Unhandled model", model)
        for chunk in llm_response:
            messages[-1].content += chunk
            yield
        messages[-1].in_progress = False
        yield
