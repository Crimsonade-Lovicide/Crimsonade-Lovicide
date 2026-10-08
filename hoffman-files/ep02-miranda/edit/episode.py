"""The Hoffman Files, ep. 2 (Miranda): the edit decision list.

Same format as ep. 1 (see ep01-hot-coffee/edit/episode.py). Kinds: blender (a 3D plate from renders/<src>, `frames`
(first, last), optional `at` anchors [(phrase, source frame)]), gfx (a card in gfx2.py), aroll (Eric on camera),
interview (a guest beat; a short slate in the story reel), hold (black and silent for `min` seconds).
No people in the 3D. The victim is never named, shown or reconstructed.
"""

SEGMENTS = [
    # ---------------------------------------------------------------- cold open
    dict(id='s01', act='Cold open', kind='blender', src='M1', frames=(1, 192), tail=0.6,
         vo="You have the right to remain silent. You've heard it on every cop show for fifty years. Here's what you "
            "haven't heard. The man those words are named after was convicted anyway. Twice. And when he was killed in a "
            "bar fight in 1976, the man police picked up for it invoked his Miranda rights, and walked out."),
    dict(id='s02', act='Cold open', kind='aroll',
         vo="I'm Eric Hoffman. I'm a lawyer. This is the case every American can recite and almost nobody knows. "
            "Let's open the file."),
    dict(id='s03', act='Cold open', kind='gfx', gfx='title', min=5.0, hit=True),

    # ---------------------------------------------------------------- act 1: the room
    dict(id='s04', act='Act 1: The room', kind='blender', src='M2', frames=(1, 192), overlay='busstop', tail=1.0,
         vo="March 1963. Phoenix. An eighteen-year-old woman finishes her shift at a movie theater, takes the bus home, "
            "and is abducted and raped on the way. We won't show her, and we won't use her name."),
    dict(id='s05', act='Act 1: The room', kind='gfx', gfx='phoenix', tail=1.0, cues=['a relative', 'Ernesto Miranda'],
         vo="About a week later, a relative spots a car that matches her description and gets part of the plate. "
            "It leads police to a man in his early twenties named Ernesto Miranda."),
    dict(id='s06', act='Act 1: The room', kind='blender', src='M3', frames=(1, 250), overlay='room', tail=0.6,
         at=[('Interrogation Room', 70), ('About two hours later', 200)],
         vo="March 13th. Detectives Carroll Cooley and Wilfred Young bring him in, put him in a lineup, then take him "
            "into Interrogation Room Number 2. About two hours later, they walk out with a signed confession."),
    dict(id='s07', act='Act 1: The room', kind='blender', src='M3', frames=(250, 288), overlay='room_hold', tail=1.4,
         vo="Nobody hit him. Nobody threatened him. And nobody told him he could stay silent, or ask for a lawyer."),
    dict(id='s08', act='Act 1: The room', kind='gfx', gfx='form', tail=1.4, cues=['already typed', 'with full knowledge', 'Nobody had told'],
         vo="Here's the detail I love as a lawyer. He wrote it on a form, and at the top, already typed, was a line "
            "certifying the statement was made 'with full knowledge of my legal rights.' Nobody had told him what those "
            "rights were."),
    dict(id='s09', act='Act 1: The room', kind='aroll',
         vo="Was that legal in 1963? In Arizona, yes. The test was whether a confession was voluntary. Not whether you "
            "knew you could refuse."),
    dict(id='s09a', act='Act 1: The room', kind='gfx', gfx='brown', tail=1.4,
         cues=['Brown v. Mississippi', 'threw those confessions out', 'case by case', 'By that test'],
         vo="That test came out of a 1936 case, Brown v. Mississippi. A deputy sheriff and others whipped three Black "
            "men until they confessed to a murder, and the Supreme Court threw those confessions out. After "
            "that, the question was whether a confession was voluntary, judged case by case: how long, how old, how "
            "educated, whether anyone made threats. No beating, no threats, two hours. By that test, Miranda's "
            "confession was fine."),

    # ---------------------------------------------------------------- act 2: convicted
    dict(id='s10', act='Act 2: Convicted', kind='gfx', gfx='docket', tail=1.2,
         cues=['objected', 'The judge overruled', 'Convicted', 'The Arizona Supreme Court'],
         vo="His court-appointed lawyer, Alvin Moore, objected to the confession. The judge overruled him. Convicted. "
            "Twenty to thirty years. The Arizona Supreme Court affirmed."),
    dict(id='s11', act='Act 2: Convicted', kind='aroll',
         vo="That should have been the end. Instead, the ACLU found the case and brought in two Phoenix lawyers, John "
            "Frank and John Flynn, who took it for free, all the way to Washington."),
    dict(id='s11a', act='Act 2: Convicted', kind='gfx', gfx='precedents', tail=1.6,
         cues=['Gideon v. Wainwright', 'Escobedo v. Illinois', 'what about the person'],
         vo="They had an opening. Five days after Miranda signed that confession, the Supreme Court decided Gideon v. "
            "Wainwright: if you're charged with a felony and can't afford a lawyer, the state has to give you one. A "
            "year later came Escobedo v. Illinois. Police had refused to let a suspect see the lawyer he was asking for, "
            "and the Court threw out his confession. That left an obvious question. If the right to a lawyer matters at "
            "trial, and matters when you ask for one at the station, what about the person who doesn't know to ask?"),
    dict(id='s12', act='Act 2: Convicted', kind='interview', guest='defense', beat=1, plan=60,
         topics=['What a signed confession does to a defense case on day one',
                 'Why a firm takes a case like this for free, all the way up']),

    # ---------------------------------------------------------------- act 3: the decision
    dict(id='s13', act='Act 3: The decision', kind='blender', src='M6', frames=(1, 190), overlay='bench', tail=5.0,
         at=[('On June 13', 24), ('five to four', 46)],
         vo="The Supreme Court bundled Miranda with three other confession cases. On June 13, 1966, it ruled five to four."),
    dict(id='s14', act='Act 3: The decision', kind='aroll',
         vo="Chief Justice Earl Warren's point was simple. The interrogation room is built to work on you. It's private, "
            "it's long, and you're alone."),
    dict(id='s14a', act='Act 3: The decision', kind='gfx', gfx='manuals', tail=1.6,
         cues=['Question him alone', 'Treat his guilt', 'Offer him', 'Play a friendly', 'The opinion called it'],
         vo="To prove it, he did something unusual. He quoted the police training manuals. Question him alone, on your "
            "ground, not his. Treat his guilt as already settled. Offer him an excuse that makes confessing easier. Play a "
            "friendly detective against a hostile one. The opinion called it a setting created for no purpose other than "
            "to subjugate the individual to the will of his examiner."),
    dict(id='s14b', act='Act 3: The decision', kind='aroll',
         vo="So before police question someone in custody, they have to tell him four things."),
    dict(id='s15', act='Act 3: The decision', kind='gfx', gfx='warnings', tail=1.6,
         cues=['You can stay silent', 'What you say', 'You can have a lawyer', "And if you can't", 'Skip the warnings'],
         vo="You can stay silent. What you say can be used against you. You can have a lawyer. And if you can't afford "
            "one, you'll get one. Skip the warnings, and what he says can't be used to prove the case."),
    dict(id='s16', act='Act 3: The decision', kind='gfx', gfx='split', tail=1.6, cues=['The four dissenters', 'Justice White wrote'],
         vo="The four dissenters said it would put guilty men back on the street. Justice White wrote that 'in some "
            "unknown number of cases the Court's rule will return a killer, a rapist or other criminal to the streets.'"),
    dict(id='s17', act='Act 3: The decision', kind='aroll',
         vo="So did it? Let's follow Ernesto Miranda."),

    # ---------------------------------------------------------------- act 4: convicted again
    dict(id='s18', act='Act 4: Convicted again', kind='gfx', gfx='retrial', tail=1.2,
         cues=['The prosecution called', 'Convicted again'],
         vo="Arizona retried him in 1967, this time without the confession. The prosecution called his former common-law "
            "wife. She testified that during a jail visit he told her what he'd done. Convicted again. Twenty to thirty years."),
    dict(id='s19', act='Act 4: Convicted again', kind='aroll',
         vo="That's the part the TV version leaves out. Miranda doesn't make evidence disappear. It takes one thing off "
            "the table: what police get out of you in that room without the warning. Everything else is still in play."),
    dict(id='s20', act='Act 4: Convicted again', kind='interview', guest='defense', beat=2, plan=75,
         topics=['What a suppression hearing actually looks like',
                 'How often a confession really gets thrown out']),

    # ---------------------------------------------------------------- act 5: the cards
    dict(id='s21', act='Act 5: The cards', kind='blender', src='M9', frames=(1, 192), overlay='cards', tail=1.2,
         at=[('he reportedly signed', 60), ('and sold them', 110)],
         vo="He was paroled in 1972. Back in Phoenix, he reportedly signed the cards police carry to read the warnings, "
            "and sold them for a dollar fifty."),
    dict(id='s22', act='Act 5: The cards', kind='blender', src='M10', frames=(1, 192), overlay='bar', tail=0.7,
         vo="January 31, 1976. A fight in a Phoenix bar. Miranda is stabbed and dies. Police pick up a suspect. He's read "
            "his rights. He invokes them. He's released. The man later charged fled to Mexico and was never tried."),
    dict(id='s23', act='Act 5: The cards', kind='hold', min=2.0),          # nothing on screen; the music stops dead

    # ---------------------------------------------------------------- act 6: is it still standing?
    dict(id='s24', act='Act 6: Is it still standing?', kind='gfx', gfx='timeline', tail=1.4,
         cues=['since the day', 'In 1968', 'In 1971', 'In 1984', 'William Rehnquist'],
         vo="Miranda has been under attack since the day it came down. In 1968, Congress passed a law to get around it: "
            "a confession was admissible as long as it was voluntary. Then the Court itself started trimming. In 1971, it "
            "said a statement taken without the warnings can still be used against you if you take the stand and tell a "
            "different story. In 1984, it carved out a public safety exception: if an officer asks where the gun is "
            "before reading the warnings, the answer comes in. That opinion was written by William Rehnquist."),
    dict(id='s24a', act='Act 6: Is it still standing?', kind='gfx', gfx='dickerson', tail=2.0,
         cues=['Dickerson', 'Instead he wrote', 'has become embedded'],
         vo="By 2000 he was Chief Justice, and the 1968 law finally reached the Court in Dickerson. Plenty of people "
            "expected him to finish Miranda off. Instead he wrote the opinion saving it, seven to two. Miranda, he wrote, "
            "'has become embedded in routine police practice to the point where the warnings have become part of our "
            "national culture.'"),
    dict(id='s25', act='Act 6: Is it still standing?', kind='aroll',
         vo="But it isn't what it was. In 2010, the Court said staying silent isn't enough; you have to say you're "
            "invoking. And in 2022, it said a Miranda violation alone doesn't let you sue the officer."),
    dict(id='s25a', act='Act 6: Is it still standing?', kind='gfx', gfx='cost', tail=1.6,
         cues=['Paul Cassell', 'Stephen Schulhofer', 'What the studies agree'],
         vo="So what does it cost? Researchers have fought over that number for decades. In 1996, Paul Cassell estimated "
            "that Miranda costs prosecutors almost four percent of all criminal cases. Stephen Schulhofer went through the "
            "same studies and got about one percent. What the studies agree on is that most suspects, about four in five, "
            "waive their rights and talk anyway."),
    dict(id='s26', act='Act 6: Is it still standing?', kind='interview', guest='counter', beat=3, plan=60,
         topics=['What Miranda costs: lost confessions, guilty people who walk', 'Is it worth it?']),

    # ---------------------------------------------------------------- the holding + outro
    dict(id='s27', act='The holding', kind='gfx', gfx='holding_title', hit=True, tail=0.8,
         vo="So what does Miranda actually stand for? Three things."),
    dict(id='s28', act='The holding', kind='gfx', gfx='holding', tail=1.4, cues=['One:', 'Two:', 'Three:'],
         vo="One: the warning isn't required at arrest. It's required before custodial interrogation. Two: the remedy "
            "is losing the statement, not losing the case. Three: the right is real, but you have to use it. Out loud."),
    dict(id='s28a', act='The holding', kind='gfx', gfx='say_it', tail=1.6,
         cues=['Maybe I should', "I'm going to remain silent", 'I want a lawyer', "That's general information"],
         vo="If you take one practical thing from this, the words matter. In 1994, the Court held that 'Maybe I should "
            "talk to a lawyer' wasn't clear enough to stop the questioning. So be clear. 'I'm going to remain silent. "
            "I want a lawyer.' Then stop talking. That's general information, not advice about your case. If you're ever "
            "in that room, that's exactly when you call one."),
    dict(id='s29', act='The holding', kind='aroll',
         vo="Ernesto Miranda was convicted twice and died in a bar fight. His name is on the most famous sentence in "
            "American law. And the right it stands for only works if you say it."),
    dict(id='s30', act='Outro', kind='aroll',
         vo="Next time: the next case. I'm Eric Hoffman, and these are The Hoffman Files."),
    dict(id='s31', act='Outro', kind='gfx', gfx='endcard', min=9.0),
]

GUESTS = {
    'defense': ('GUEST NAME', 'CRIMINAL DEFENSE ATTORNEY'),
    'counter': ('GUEST NAME', 'COUNTERPOINT  ·  MIRANDA CRITIC'),
}
HOST = ('ERIC HOFFMAN', 'ATTORNEY · HOST')

INTERVIEW_SLATE = 7.0
