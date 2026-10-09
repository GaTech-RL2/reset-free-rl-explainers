from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def chapter(title, visual, steps, narration, source):
    paragraphs = [p.strip() for p in narration.strip().split('\n\n') if p.strip()]
    assert len(paragraphs) == len(steps) == 3, title
    return dict(title=title, visual=visual,
                steps=[dict(title=a, math=b, explain=c) for a,b,c in steps],
                paragraphs=paragraphs, narration='\n\n'.join(paragraphs), source=source)

def episode(id, number, short, title, paper, authors, year, url, color, summary, sources, chapters):
    return dict(id=id, number=f'{number:02}', short=short, title=title, paper=paper,
                authors=authors, year=year, url=url, color=color, summary=summary,
                sources=sources, chapters=chapters, target_duration=840)
