from fasthtml.common import *

from model import Router

hdrs = (
    Link(
        rel="stylesheet",
        href="https://cdnjs.cloudflare.com/ajax/libs/flexboxgrid/6.3.1/flexboxgrid.min.css",
        type="text/css",
    ),
    MarkdownJS(),
    HighlightJS(langs=["python", "javascript", "html", "css"]),
)

db = database("routers.db")
routers = db.create(Router, pk="index")

app = FastHTML(pico=True, hdrs=hdrs)

count = 0


@app.get("/")
def home():
    return Title("Count Demo"), Main(
        H1("Count Demo"),
        P(f"Count is set to {count}", id="count"),
        Button(
            "Increment", hx_post="/increment", hx_target="#count", hx_swap="innerHTML"
        ),
        Ul(
            Li(A("markdown demo", href="/markdown")),
            Li(A("router form", href="/router_form")),
        ),
    )


@app.get("/markdown")
def markdown():
    content = """
    # header 1

    ## header 2

    list
    - item 1
    - item 2
    **bold text**
    *italic text*
    """
    return Div(H2("Markdown Demo"), Div(content, cls="marked"))


@app.post("/increment")
def increment():
    print("incrementing")
    global count
    count += 1
    return f"Count is set to {count}"


router_form = (
    Form(method="post", action="/router")(
        Div(
            Div(
                H2("Router Configuration"),
                Fieldset(
                    Div(
                        Label("Index", cls="col-xs-4"),
                        Input(name="index", cls="col-xs-8"),
                        cls="row",
                    ),
                    Div(
                        Label("IPs", cls="col-xs-4"),
                        Input(name="ips", cls="col-xs-8"),
                        cls="row",
                    ),
                    Div(
                        Label("Loopbacks", cls="col-xs-4"),
                        Input(name="loopbacks", cls="col-xs-8"),
                        cls="row",
                    ),
                    Div(
                        Label("User", cls="col-xs-4"),
                        Input(name="user", cls="col-xs-8"),
                        cls="row",
                    ),
                    Div(
                        Label("Password", cls="col-xs-4"),
                        Input(name="password", type="text", cls="col-xs-8"),
                        cls="row",
                    ),
                    Div(
                        Label("Secret", cls="col-xs-4"),
                        Input(name="secret", type="text", cls="col-xs-8"),
                        cls="row",
                    ),
                ),
                Br(),
                Button("Save", type="submit"),
            ),
        )
    ),
)


def configured(router_keys):
    return Div(
        H2("Configured Routers"),
        Ul(
            *[Li(A(f"Router {k}", href=f"/router_view/{k}")) for k in router_keys],
        ),
    )


@app.get("/router_form")
def router_form_view():
    r_keys = [k.index for k in routers()]
    return Div(
        Div(
            A("Home", href="/"),
            router_form,
            configured(r_keys),
            cls="col-xs-6",
        ),
        cls="container",
    )


@app.get("/router_view/{index}")
def get_router(index: int):
    router = routers.get(index)
    if not router:
        return "Router not found"
    return Div(
        H2(f"Router {router.index}"),
        P(f"IPs: {router.ips}"),
        P(f"Loopbacks: {router.loopbacks}"),
        P(f"User: {router.user}"),
        P(f"Password: {router.password}"),
        P(f"Secret: {router.secret}"),
        A("Back", href=f"/router_form"),
    )


@app.post("/router")
def save_router(router: Router):
    exists = router.index in routers
    if exists:
        routers.update(router)
    else:
        routers.insert(router)
    return RedirectResponse(url=f"/router_view/{router.index}", status_code=303)


serve(port=8000)
