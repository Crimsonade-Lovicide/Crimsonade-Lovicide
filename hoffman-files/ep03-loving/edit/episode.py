"""Ep. 3 Loving v. Virginia: the beat list. One entry per beat, in reel order. The text matches the Script draft in
the Episode 3 production doc; the fact numbers point at its Fact base. Kinds: 'aroll' is Eric on camera (blue
Background effect), 'vo' is voice-over over 3D or a card, 'card' is a title or end card with no voice."""

BEATS = [
    # Cold open
    dict(id='s01', act='Cold open', kind='vo', facts=[12, 14, 15],
         picture='3D: a bedroom door at night, a flashlight beam under it',
         vo="June 1958. A bricklayer and his wife drive home to Caroline County, Virginia, from their wedding in "
            "Washington. Five weeks later, before dawn, the sheriff and two deputies come through their bedroom door."),
    dict(id='s02', act='Cold open', kind='vo', facts=[15, 16],
         picture='3D: the framed certificate on the wall, the beam finds it',
         vo="She points at the marriage certificate on the wall. “I’m his wife.” The sheriff says, “Not here you’re not.”"),
    dict(id='s03', act='Cold open', kind='aroll', facts=[19, 32],
         picture='On camera',
         vo="I’m Eric Hoffman. I’m a lawyer. You know this case by its name, and you probably think you know the story: "
            "a brave couple, a dramatic trial, a Supreme Court that struck down racist laws. Most of that is wrong. "
            "There was no trial. They pleaded guilty. And Virginia’s argument wasn’t that the races were unequal. "
            "It was that the law was fair. Let’s open the file."),
    dict(id='s04', act='Title', kind='card', facts=[],
         picture='Title card: THE HOFFMAN FILES · Loving v. Virginia · 388 U.S. 1 (1967). Theme in.', vo=''),
    # Act one: the crime
    dict(id='s05', act='Act one: the crime', kind='vo', facts=[2, 3, 4],
         picture='Card: § 20-58, the text',
         vo="Here is the crime. Not being married. Leaving the state to get married, and coming back. Section 20-58 of "
            "the Virginia Code: if a white person and a colored person go out of the state to marry, and return to live "
            "together as husband and wife, they are punished as if the marriage had happened in Virginia. Section 20-59 "
            "makes it a felony. One to five years in the penitentiary. And section 20-57 says the marriage itself is "
            "void. No divorce needed. It never existed."),
    dict(id='s06', act='Act one: the crime', kind='vo', facts=[5, 1],
         picture='Card: 1691 · 1924 · 1958 on a timeline',
         vo="Virginia had banned marriages like this since the colonial era. The version on the books in 1958 was the "
            "Racial Integrity Act of 1924. It defined “white” so tightly that a single exception had to be written in, "
            "for descendants of Pocahontas."),
    dict(id='s07', act='Act one: the crime', kind='vo', facts=[10, 11, 12, 13],
         picture='3D: Central Point, a frame house, lights on downstairs',
         vo="Richard Loving was twenty-four, white, a construction worker. Mildred Jeter was eighteen. The court record "
            "calls her “a colored person.” Later in life she said she was Indian, Rappahannock. They had both grown up "
            "in Central Point, a crossroads where the color line had always been blurry. They drove to Washington on "
            "June 2, 1958, married, and came home to live downstairs at her parents’ house."),
    dict(id='s08', act='Act one: the crime', kind='vo', facts=[14, 17],
         picture='3D: the Bowling Green jail, a cell door',
         vo="The warrants were sworn on July 11. The arrest came in the middle of the night. They were taken to the jail "
            "at Bowling Green. Richard was out the next day on a thousand-dollar bond. Mildred stayed several more days, "
            "and was released to her father."),
    # Act two: the plea
    dict(id='s09', act='Act two: the plea', kind='vo', facts=[18, 19, 22],
         picture='3D: the Caroline County courthouse, empty bench',
         vo="In October a grand jury indicted them. On January 6, 1959, they stood in front of Judge Leon Bazile. "
            "There was no trial. They pleaded guilty."),
    dict(id='s10', act='Act two: the plea', kind='aroll', facts=[2, 19],
         picture='On camera',
         vo="Why plead guilty? Because they were guilty. They had left the state to marry and come back. Those were the "
            "only facts the statute cared about, and nobody disputed them. A trial would have proved what everyone "
            "already knew. The only question was the sentence."),
    dict(id='s11', act='Act two: the plea', kind='vo', facts=[20],
         picture='Card: the sentence, verbatim',
         vo="One year each in jail. Suspended for twenty-five years, on one condition. Read it. “That both accused leave "
            "Caroline County and the state of Virginia at once and do not return together or at the same time to said "
            "county and state for a period of twenty-five years.” Banishment. They could come back to Virginia. Just "
            "never together."),
    dict(id='s12', act='Act two: the plea', kind='vo', facts=[21, 23, 24],
         picture='Card: $36.29',
         vo="They paid thirty-six dollars and twenty-nine cents each in court costs and moved to Washington, to a "
            "cousin’s house on Neal Street. They had three children. Mildred went home to Central Point to give birth, "
            "alone, because the sentence allowed it."),
    dict(id='s13', act='Act two: the plea', kind='vo', facts=[25],
         picture='3D: a letter on a kitchen table, an envelope addressed to the Attorney General',
         vo="Five years went by. In 1963 Mildred Loving wrote a letter to the Attorney General of the United States, "
            "Robert Kennedy. She said later she wasn’t in anything to do with civil rights. “We were trying to get back "
            "to Virginia. That was our goal, to get back home.” Kennedy’s office sent her to the ACLU. The ACLU sent her "
            "a young lawyer in Alexandria named Bernard Cohen."),
    # Act three: the judge
    dict(id='s14', act='Act three: the judge', kind='vo', facts=[26, 27],
         picture='Card: Motion to Vacate · Nov 6, 1963',
         vo="Cohen’s problem was that the case was over. They had pleaded guilty four years earlier and never appealed. "
            "So he went back to the same judge with a motion to vacate the sentence, and asked Judge Bazile to hold his "
            "own ruling unconstitutional. The judge took fourteen months to answer."),
    dict(id='s15', act='Act three: the judge', kind='vo', facts=[27],
         picture='Card: the Bazile quotation, verbatim, attributed, Jan 22, 1965',
         vo="On January 22, 1965, he denied the motion. This is what he wrote. “Almighty God created the races white, "
            "black, yellow, malay and red, and he placed them on separate continents. And but for the interference with "
            "his arrangement there would be no cause for such marriages. The fact that he separated the races shows "
            "that he did not intend for the races to mix.”"),
    dict(id='s16', act='Act three: the judge', kind='aroll', facts=[8, 27],
         picture='On camera',
         vo="I want to be careful here. That paragraph is famous because the Supreme Court quoted it, and it sounds like "
            "the whole case. It isn’t. Bazile’s opinion was a trial judge’s opinion. The legal fight was about "
            "something colder: a theory of equality that had been the law of the United States for eighty-two years."),
    dict(id='s17', act='Act three: the judge', kind='vo', facts=[8, 9, 28],
         picture='Card: Pace v. Alabama (1883) · “equal application”',
         vo="In 1883 the Supreme Court upheld an Alabama law that punished interracial couples more harshly than anyone "
            "else. The reasoning: the law punished the white partner and the Black partner exactly the same, so nobody "
            "was being treated unequally. Equal application. Virginia’s highest court had used the same logic in 1955 "
            "to uphold these statutes, and in March 1966 it used it again on the Lovings. It affirmed the convictions. "
            "It did strike one thing: the banishment. Twenty-five years of exile, the court said, was “unreasonable.” "
            "So it sent the case back to be resentenced. Which, by the way, under the statute, meant the penitentiary."),
    # Act four: the argument
    dict(id='s18', act='Act four: the argument', kind='vo', facts=[29, 30, 35],
         picture='3D: the Supreme Court courtroom, empty, the lectern',
         vo="April 10, 1967. The Lovings did not come to Washington for the argument. They stayed on a farm in King and "
            "Queen County and avoided reporters. Their lawyers split the case: Philip Hirschkop argued equal protection, "
            "Bernard Cohen argued due process."),
    dict(id='s19', act='Act four: the argument', kind='vo', facts=[32, 38],
         picture='Card: Virginia’s argument, two lines',
         vo="Then Virginia. Assistant Attorney General R. D. McIlwaine made two arguments, and you should hear them as he "
            "made them. First: the law applies equally to both races, so it is not discrimination. Second: even if the "
            "Court looked past that, the legislature had a legitimate reason. He cited studies. Mixed marriages, he "
            "said, carried “sociological and psychological evils” for the families and especially the children, and "
            "the state was entitled to protect them."),
    dict(id='s20', act='Act four: the argument', kind='aroll', facts=[32, 37],
         picture='On camera',
         vo="That second argument is the one that should bother you, because it is the shape of every argument like it. "
            "Not “these people are inferior,” but “we are protecting the children.” It sounds reasonable. The Court’s "
            "answer was that it did not matter how reasonable it sounded, because the law drew its line by race and "
            "nothing else."),
    dict(id='s21', act='Act four: the argument', kind='vo', facts=[31],
         picture='Card: the Richard Loving line, attributed to Cohen, Apr 10, 1967 (verified)',
         vo="Cohen ended with something his client had said to him. “No one can articulate it better than Richard Loving "
            "when he said to me, Mr. Cohen, tell the Court I love my wife and it is just unfair that I can’t live with "
            "her in Virginia.”"),
    # The holding
    dict(id='s22', act='The holding', kind='vo', facts=[36, 38, 37],
         picture='Card: June 12, 1967 · 9 to 0',
         vo="June 12, 1967. Nine to nothing. Chief Justice Warren wrote it. First, equal application: rejected. The Court "
            "said the mere equal application of a law containing racial classifications does not take it outside the "
            "Fourteenth Amendment. The eighty-four-year-old theory was dead. Second, the purpose. The Court found “no "
            "legitimate overriding purpose independent of invidious racial discrimination,” and called the statutes "
            "“measures designed to maintain White Supremacy.” Those are the Court’s words."),
    dict(id='s23', act='The holding', kind='vo', facts=[39],
         picture='Card: the due process line, verbatim',
         vo="And then the sentence this case is remembered for. “The freedom to marry has long been recognized as one of "
            "the vital personal rights essential to the orderly pursuit of happiness by free men.” The freedom to marry "
            "a person of another race, the Court said, “resides with the individual and cannot be infringed by the "
            "State.”"),
    dict(id='s24', act='The holding', kind='vo', facts=[6, 7, 44],
         picture='Card/3D: map, sixteen states lit, going dark',
         vo="Sixteen states still had these laws that morning. By nightfall none of them were enforceable. Alabama left "
            "the words in its constitution anyway, until the voters took them out in the year 2000."),
    dict(id='s25', act='The holding', kind='vo', facts=[40, 41, 42, 43],
         picture='3D: Central Point, the house, dusk',
         vo="Mildred Loving gave one short news conference at her lawyers’ office. “I feel free now.” Someone burned a "
            "cross in her mother’s yard. Richard built them a house in Central Point. He died there eight years later, "
            "when a drunk driver hit his car. She lived in that house until 2008."),
    # Outro
    dict(id='s26', act='Outro', kind='aroll', facts=[45],
         picture='On camera',
         vo="Three things to take from the file. One: the crime was crossing a state line. The marriage was legal where "
            "they made it. Two: the state’s case was not that the races were unequal. It was that the law was fair "
            "because it hurt everyone the same, and the Supreme Court had agreed with that for eighty years. Loving is "
            "the case that ended it. Three: the line about the freedom to marry is the reason this case is still argued "
            "about. It was the foundation of Obergefell in 2015. What that means going forward is a question for another "
            "file. This one is closed."),
    dict(id='s27', act='End card', kind='card', facts=[],
         picture='End card: THE HOFFMAN FILES · LAW BY LAWYERS · sources · general legal information, not legal advice',
         vo=''),
]

WPM = 150   # planning pace; the cut retimes to the takes


def secs(b):
    return len(b['vo'].split()) * 60 / WPM
