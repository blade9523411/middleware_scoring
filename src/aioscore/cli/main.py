import typer, json
from aioscore.contracts.validator import validate_stream
from aioscore.normalization.apply import normalize_stream
from aioscore.scoring.final import score_stream

app = typer.Typer(add_completion=False, help="AI Opportunity Score CLI")

@app.command()
def validate(inp: str, stop_on_error: bool=False):
    ok = validate_stream(inp, stop_on_error=stop_on_error)
    raise typer.Exit(code=0 if ok else 1)

@app.command()
def norm(inp: str, norm: str, out: str):
    normalize_stream(inp, norm, out)

@app.command()
def score(inp: str, weights: str, out: str):
    score_stream(inp, weights, out)

if __name__ == "__main__":
    app()
