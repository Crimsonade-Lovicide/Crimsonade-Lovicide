"""The Hoffman Files, ep. 1 (The Hot Coffee Case): the edit decision list.

One entry per beat of the script, in order. `vo` is Eric's line exactly as scripted; the story reel reads it
with a temporary synthetic voice so pacing can be judged before the shoot. Kinds:
  blender    a 3D reconstruction plate (renders/<src>), with `frames` (first, last) and optional time-map
             anchors `at` = [(phrase in the VO, source frame), ...] so actions land on the words
  gfx        a motion-graphics card drawn in gfx.py (function named by `gfx`)
  aroll      Eric on camera (a slate in the story reel; the editor drops the take here)
  interview  a guest beat (a short slate in the story reel; `plan` is the planned length in seconds)
Every number on screen traces to the fact base in the episode doc.
"""

SEGMENTS = [
    # ---------------------------------------------------------------- cold open
    dict(id='s01', act='Cold open', kind='blender', src='E1', frames=(1, 192), min=9.0,
         vo="A woman spills McDonald's coffee on herself and sues. A jury gives her nearly three million dollars. "
            "You've heard this one. It's been a punchline for thirty years."),
    dict(id='s02', act='Cold open', kind='aroll',
         vo="I'm Eric Hoffman. I'm a lawyer, and almost everything you think you know about this case is wrong. "
            "Not because of spin. Because of the trial record. Let's open the file."),
    dict(id='s03', act='Cold open', kind='gfx', gfx='title', min=5.0, hit=True),

    # ---------------------------------------------------------------- act 1: the joke
    dict(id='s04', act='Act 1: The joke', kind='gfx', gfx='headline', tail=1.0,
         vo="Here's the version most of us got. Careless customer. Of course coffee is hot, it's coffee. "
            "Greedy lawsuit, runaway jury, lottery ticket."),
    dict(id='s05', act='Act 1: The joke', kind='aroll',
         vo="It showed up on late-night TV, in a Seinfeld episode, and for years in arguments about lawsuit abuse. "
            "What almost never came with it was the facts. So here they are."),

    # ---------------------------------------------------------------- act 2: the spill
    dict(id='s06', act='Act 2: The spill', kind='blender', src='E2', frames=(1, 144), overlay='car',
         vo="February 27, 1992. Albuquerque, New Mexico. Stella Liebeck is 79. She's in the passenger seat of her "
            "grandson's car, a 1989 Ford Probe. No cup holders."),
    dict(id='s07', act='Act 2: The spill', kind='blender', src='E3', frames=(1, 168), overlay='recon', tail=2.2,
         at=[('She puts the cup', 40), ('pulls the lid', 62), ('The whole cup', 102)],
         vo="They've just bought breakfast at a drive-through, and he's parked so she can add cream and sugar. "
            "She puts the cup between her knees and pulls the lid toward her. The whole cup goes into her lap."),
    dict(id='s08', act='Act 2: The spill', kind='blender', src='E3', frames=(168, 240), overlay='recon_soak', tail=1.0,
         vo="She was wearing cotton sweatpants. They soaked up the coffee and held it against her skin."),

    # ---------------------------------------------------------------- act 3: the injuries
    dict(id='s09', act='Act 3: The injuries', kind='blender', src='E4', frames=(1, 288), overlay='skin', tail=1.2,
         at=[('Third degree means', 150), ('every layer', 270)],
         vo="This is where the joke falls apart. Third-degree burns on six percent of her skin, and lesser burns "
            "over sixteen percent. Third degree means full thickness: the burn goes through every layer."),
    dict(id='s10', act='Act 3: The injuries', kind='gfx', gfx='injuries', tail=1.0,
         cues=['Eight days', 'Skin grafts', 'She lost', 'Two years'],
         vo="Eight days in the hospital. Skin grafts. She lost about twenty pounds, down to eighty-three. "
            "Two years of treatment."),
    dict(id='s11', act='Act 3: The injuries', kind='gfx', gfx='temperature', tail=1.2,
         cues=["McDonald's own standard", 'at 190', 'At 180'],
         vo="Why so bad? Temperature. McDonald's own standard was to hold its coffee at 180 to 190 degrees. "
            "An expert testified that at 190, liquid can cause a third-degree burn in about three seconds. "
            "At 180, about twelve to fifteen."),
    dict(id='s12', act='Act 3: The injuries', kind='aroll',
         vo="Coffee tested elsewhere in town was at least twenty degrees cooler."),

    # ---------------------------------------------------------------- act 4: the $800
    dict(id='s13', act='Act 4: The $800', kind='gfx', gfx='ledger', tail=0.6,
         cues=['her medical bills', 'some future care', 'the income her daughter lost', 'About twenty thousand'],
         vo="Here's the part nobody tells you. She didn't start by suing. She asked McDonald's to cover her costs: "
            "her medical bills, some future care, and the income her daughter lost caring for her. "
            "About twenty thousand dollars."),
    dict(id='s14', act='Act 4: The $800', kind='gfx', gfx='offer', tail=2.4,
         vo="McDonald's offered eight hundred."),
    dict(id='s15', act='Act 4: The $800', kind='interview', guest='morgan', beat=1, plan=60,
         topics=['How the case reached him', 'Why take a case whose client had asked for $20,000']),
    dict(id='s16', act='Act 4: The $800', kind='aroll',
         vo="That's when she hired a lawyer. He offered to settle for three hundred thousand. A mediator suggested "
            "two hundred twenty-five thousand. McDonald's said no. So it went to a jury."),

    # ---------------------------------------------------------------- act 5: the trial
    dict(id='s17', act='Act 5: The trial', kind='blender', src='E7', frames=(1, 288), overlay='folders', tail=1.0,
         at=[('Between 1982', 12), ('more than seven hundred', 222)],
         vo="August 1994. The trial runs about a week and a half, and the jury learns something that changes the "
            "case. Between 1982 and 1992, McDonald's received more than seven hundred reports of people burned by "
            "its coffee."),
    dict(id='s18', act='Act 5: The trial', kind='gfx', gfx='claims', tail=1.0,
         vo="The company had already paid more than half a million dollars settling burn claims."),
    dict(id='s19', act='Act 5: The trial', kind='gfx', gfx='qa', tail=1.0,
         vo="Its quality-assurance manager testified. In substance, his position was that seven hundred reports "
            "weren't enough to make the company change how it served coffee."),
    dict(id='s20', act='Act 5: The trial', kind='aroll',
         vo="Put yourself in the jury box. The question isn't whether coffee should be hot. It's whether this "
            "company knew its coffee was hot enough to do this, kept serving it that way, and decided that was an "
            "acceptable cost."),
    dict(id='s21', act='Act 5: The trial', kind='gfx', gfx='fault', tail=1.2,
         cues=['twenty percent of the fault', 'two hundred thousand', 'one hundred sixty'],
         vo="The jury said yes. But they didn't find her blameless. They put twenty percent of the fault on her. "
            "So her compensatory damages, two hundred thousand, were cut by twenty percent, to one hundred sixty "
            "thousand."),
    dict(id='s22', act='Act 5: The trial', kind='interview', guest='morgan', beat=2, plan=75,
         topics=['What the jury reacted to most', 'How he arrived at "two days of coffee sales"']),
    dict(id='s23', act='Act 5: The trial', kind='blender', src='E9', frames=(1, 192), overlay='sales', tail=1.6,
         at=[('two days', 12), ('1.35 million', 96), ('2.7 million', 180)],
         vo="Then punitive damages. Her lawyer suggested a number tied to the company's own sales: two days of "
            "McDonald's coffee revenue, about 1.35 million dollars a day. The jury awarded 2.7 million."),

    # ---------------------------------------------------------------- act 6: after the verdict
    dict(id='s24', act='Act 6: After the verdict', kind='aroll',
         vo="That's the number that made the news. Here's what happened next, which almost never did."),
    dict(id='s25', act='Act 6: After the verdict', kind='gfx', gfx='shrink', tail=1.4,
         cues=['four hundred eighty', 'three times', 'Total'],
         vo="The judge cut the punitive damages to four hundred eighty thousand, three times the compensatory "
            "award. Total: six hundred forty thousand dollars."),
    dict(id='s26', act='Act 6: After the verdict', kind='gfx', gfx='settled', tail=1.0,
         vo="Both sides were headed for appeal. Instead they settled, confidentially. Nobody outside knows the final "
            "number, and anyone who tells you they do is guessing."),
    dict(id='s27', act='Act 6: After the verdict', kind='gfx', gfx='died', tail=1.6,
         vo="Stella Liebeck died in 2004. She was ninety-one. Her daughter said the settlement paid for a live-in "
            "nurse. By then, the story had a life of its own."),
    dict(id='s28', act='Act 6: After the verdict', kind='interview', guest='counter', beat=3, plan=45,
         topics=["The strongest argument McDonald's had", 'Was $2.7 million in punitive damages defensible?']),

    # ---------------------------------------------------------------- the holding + outro
    dict(id='s29', act='The holding', kind='gfx', gfx='holding_title', hit=True, tail=0.8,
         vo="So what does this case actually stand for? Not 'you can get rich spilling coffee.' Three things."),
    dict(id='s30', act='The holding', kind='gfx', gfx='holding', tail=1.4,
         cues=['One:', 'Two:', 'Three:'],
         vo="One: comparative fault. The jury put twenty percent of the blame on her, and her award shrank to match. "
            "Two: punitive damages are about what a company knew and did. Seven hundred prior reports were the case. "
            "Three: the system has brakes. A judge cut the punitive award by more than eighty percent."),
    dict(id='s31', act='The holding', kind='aroll',
         vo="The headline was a spilled cup of coffee. The record was a 79-year-old woman with full-thickness burns, "
            "a company that had heard it seven hundred times, and an eight-hundred-dollar offer."),
    dict(id='s32', act='Outro', kind='aroll',
         vo="Next time: a case every cop show quotes and almost nobody knows. Miranda. I'm Eric Hoffman, and these "
            "are The Hoffman Files."),
    dict(id='s33', act='Outro', kind='gfx', gfx='endcard', min=8.0),
]

GUESTS = {
    'morgan': ('S. REED MORGAN', 'TRIAL COUNSEL FOR STELLA LIEBECK'),
    'counter': ('GUEST NAME', 'DEFENSE-SIDE / TORT-REFORM ATTORNEY'),
}
HOST = ('ERIC HOFFMAN', 'ATTORNEY · HOST')

# planned interview lengths stand in as short slates in the story reel so it stays watchable
INTERVIEW_SLATE = 7.0
