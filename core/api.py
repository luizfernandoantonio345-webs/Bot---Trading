from fastapi import FastAPI
from state_utils import load_state, save_state

app = FastAPI(title="Bot Trading API")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/state")
def get_state():
    return load_state()


@app.post("/pause")
def pause_bot():
    state = load_state()
    state["bot"]["status"] = "PAUSED"
    save_state(state)
    return {"msg": "bot pausado"}


@app.post("/resume")
def resume_bot():
    state = load_state()
    state["bot"]["status"] = "RUNNING"
    save_state(state)
    return {"msg": "bot em execução"}
