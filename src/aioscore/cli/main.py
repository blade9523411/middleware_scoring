import typer
from aioscore.contracts.validator import validate_stream
from aioscore.normalization.apply import normalize_stream
from aioscore.scoring.final import score_stream

app = typer.Typer(add_completion=False, help="AI Opportunity Score CLI")

@app.command("validate")
def cmd_validate(
    inp: str = typer.Argument(..., metavar="INP", help="Path to companies.jsonl"),
    stop_on_error: bool = typer.Option(False, "--stop-on-error", help="Stop on first validation error", is_flag=True),
):
    ok = validate_stream(inp, stop_on_error=stop_on_error)
    raise typer.Exit(code=0 if ok else 1)

@app.command("norm")
def cmd_norm(
    inp: str = typer.Argument(..., metavar="INP", help="Path to companies.jsonl"),
    norm_path: str = typer.Argument(..., metavar="NORM_CTX", help="Path to NormContext JSON"),
    out: str = typer.Argument(..., metavar="OUT", help="Where to write normalized features JSONL"),
):
    normalize_stream(inp, norm_path, out)

@app.command("score")
def cmd_score(
    inp: str = typer.Argument(..., metavar="INP", help="Normalized features JSONL"),
    weights: str = typer.Argument(..., metavar="WEIGHTS", help="weights.yaml"),
    out: str = typer.Argument(..., metavar="OUT", help="Scores JSONL"),
):
    score_stream(inp, weights, out)

# mount batch subcommands
from .batch import app as batch_app
app.add_typer(batch_app, name="batch")

if __name__ == "__main__":
    app()
