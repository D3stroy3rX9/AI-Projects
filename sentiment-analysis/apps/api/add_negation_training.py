"""
Add specialized training data for negations, edge cases, and nuanced language

This addresses the model's weakness with:
- Negations ("not bad" should be positive)
- Double negatives
- Subtle expressions
- Idiomatic phrases
- Context-dependent language
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from db import SessionLocal, TrainingData
from db.models import SentimentLabelEnum

def generate_negation_samples():
    """
    Generate ~2000 samples focused on negations and edge cases
    """

    samples = []

    # === POSITIVE NEGATIONS (500 samples) ===
    # "not bad" = good, "not terrible" = okay/good

    positive_negations = [
        "This product is not bad at all",
        "Not terrible, actually quite good",
        "Can't complain about the quality",
        "Won't disappoint you",
        "Not a bad purchase",
        "Doesn't fail to impress",
        "Can't say anything negative",
        "Nothing to complain about",
        "Not disappointed with this",
        "Can't go wrong with this choice",
        "Doesn't disappoint",
        "Not a waste of money",
        "Can't fault the quality",
        "Won't regret buying this",
        "Not as bad as I expected",
        "Better than I thought it would be",
        "Exceeds what I expected",
        "Not shabby at all",
        "Can't beat the price",
        "Won't find better quality elsewhere",
        "Not half bad actually",
        "Couldn't be happier with it",
        "Can't imagine anything better",
        "Won't let you down",
        "Not sorry I bought this",
        "Doesn't leave much to be desired",
        "Can't really criticize anything",
        "Not regretting this purchase",
        "Won't hesitate to buy again",
        "Not bad for the price",
        "Can't deny it's good quality",
        "Doesn't miss the mark",
        "Won't be returning this",
        "Not a bad deal at all",
        "Can't find any major flaws",
        "Doesn't fall short of expectations",
        "Won't be disappointed",
        "Not what I'd call poor quality",
        "Can't argue with the results",
        "Doesn't lack in quality",
        "Won't question the value",
        "Not inferior to competitors",
        "Can't overlook the quality",
        "Doesn't underperform",
        "Won't need to replace anytime soon",
        "Not uncomfortable to use",
        "Can't ignore how good this is",
        "Doesn't feel cheap",
        "Won't struggle with this",
        "Not difficult to recommend",
        "Can't stop using it",
        "Doesn't have any dealbreakers",
        "Won't be the last one I buy",
        "Not unpleasant experience",
        "Can't believe how good it is",
        "Doesn't require any improvements",
        "Won't need anything else",
        "Not poorly made",
        "Can't see myself without it now",
        "Doesn't come with any issues",
        "Won't cause any problems",
        "Not unimpressive",
        "Can't recommend it enough",
        "Doesn't disappoint in any way",
        "Won't be my last purchase from them",
        "Not underwhelming at all",
        "Can't think of anything negative",
        "Doesn't have drawbacks",
        "Won't look elsewhere next time",
        "Not subpar in quality",
        "Can't express how satisfied I am",
        "Doesn't leave you wanting more",
        "Won't break the bank either",
        "Not lacking anything important",
        "Can't fault it really",
        "Doesn't seem overpriced",
        "Won't waste your money",
        "Not unsatisfactory",
        "Can't help but love it",
        "Doesn't feel like a compromise",
        "Won't collect dust",
        "Not badly designed",
        "Can't imagine being without it",
        "Doesn't require much learning",
        "Won't cause frustration",
        "Not uncomfortable at all",
        "Can't believe the value",
        "Doesn't take long to appreciate",
        "Won't be needing a replacement",
        "Not unreliable",
        "Can't say I'm not impressed",
        "Doesn't feel like settling",
        "Won't be returning it",
        "Not poorly constructed",
        "Can't find better alternatives",
        "Doesn't seem fragile",
        "Won't regret the investment",
        "Not unsuitable for my needs",
        "Can't deny the quality",
        "Doesn't appear cheaply made",
        "Won't be switching brands",
        "Not unworthy of the price",
    ]

    for text in positive_negations:
        samples.append((text, "positive"))
        # Add variations
        samples.append((f"Honestly, {text.lower()}", "positive"))
        samples.append((f"{text}. Would recommend", "positive"))
        samples.append((f"Surprised - {text.lower()}", "positive"))
        samples.append((f"{text}. Pretty satisfied", "positive"))

    # === NEGATIVE NEGATIONS (500 samples) ===
    # "not good" = bad, "not impressed" = disappointed

    negative_negations = [
        "This is not good at all",
        "Not impressed with the quality",
        "Can't recommend this product",
        "Won't be buying this again",
        "Not worth the money",
        "Doesn't work as advertised",
        "Can't believe how poor this is",
        "Nothing impressive about it",
        "Not satisfied with my purchase",
        "Can't say I'm happy with it",
        "Won't last very long",
        "Not up to standard",
        "Can't justify the price",
        "Doesn't meet expectations",
        "Won't work for most people",
        "Not what I was hoping for",
        "Can't overlook the flaws",
        "Doesn't deliver on promises",
        "Won't recommend to others",
        "Not a good investment",
        "Can't ignore the problems",
        "Doesn't feel premium",
        "Won't hold up over time",
        "Not pleased with the quality",
        "Can't say it's worth it",
        "Doesn't seem durable",
        "Won't buy from this brand again",
        "Not happy with performance",
        "Can't understand the hype",
        "Doesn't live up to reviews",
        "Won't stand the test of time",
        "Not as described",
        "Can't get it to work properly",
        "Doesn't feel worth the price",
        "Won't survive regular use",
        "Not recommended",
        "Can't see the value",
        "Doesn't compare to alternatives",
        "Won't repurchase",
        "Not built to last",
        "Can't trust the quality",
        "Doesn't perform well",
        "Won't meet your needs",
        "Not reliable at all",
        "Can't depend on it",
        "Doesn't work half the time",
        "Won't function as expected",
        "Not sturdy enough",
        "Can't handle daily use",
        "Doesn't hold together well",
        "Won't withstand much",
        "Not impressed by the build",
        "Can't see this lasting",
        "Doesn't feel solid",
        "Won't be durable",
        "Not worth the investment",
        "Can't say it's quality",
        "Doesn't justify the cost",
        "Won't provide good value",
        "Not a smart purchase",
        "Can't recommend in good conscience",
        "Doesn't work for me",
        "Won't solve your problem",
        "Not effective at all",
        "Can't achieve desired results",
        "Doesn't do what it claims",
        "Won't improve anything",
        "Not functional enough",
        "Can't perform basic tasks",
        "Doesn't operate smoothly",
        "Won't function reliably",
        "Not user-friendly",
        "Can't figure out how to use it",
        "Doesn't have clear instructions",
        "Won't be easy to use",
        "Not intuitive at all",
        "Can't navigate the features",
        "Doesn't make sense",
        "Won't be straightforward",
        "Not well designed",
        "Can't appreciate the layout",
        "Doesn't look appealing",
        "Won't fit my decor",
        "Not aesthetically pleasing",
        "Can't stand the appearance",
        "Doesn't match description",
        "Won't look like the pictures",
        "Not what was advertised",
        "Can't believe the difference",
        "Doesn't resemble the images",
        "Won't arrive as expected",
        "Not packaged well",
        "Can't believe it arrived damaged",
        "Doesn't come protected",
        "Won't survive shipping",
        "Not in good condition",
        "Can't accept this quality",
        "Doesn't seem new",
        "Won't pass as unused",
        "Not clean or fresh",
        "Can't tell if it's genuine",
    ]

    for text in negative_negations:
        samples.append((text, "negative"))
        # Add variations
        samples.append((f"Unfortunately, {text.lower()}", "negative"))
        samples.append((f"{text}. Very disappointed", "negative"))
        samples.append((f"Sadly, {text.lower()}", "negative"))
        samples.append((f"{text}. Waste of money", "negative"))

    # === NEUTRAL NEGATIONS (300 samples) ===
    # "not great, not terrible" = okay/neutral

    neutral_negations = [
        "Not great, not terrible either",
        "Can't say it's amazing or awful",
        "Won't blow you away but it works",
        "Not exceptional but not bad",
        "Doesn't stand out much",
        "Can't complain but not thrilled",
        "Not impressive but does the job",
        "Won't wow you but it's adequate",
        "Not remarkable in any way",
        "Can't say much either way",
        "Doesn't excel or disappoint",
        "Won't be everyone's favorite",
        "Not outstanding but functional",
        "Can't call it special",
        "Doesn't have unique features",
        "Won't turn heads",
        "Not memorable",
        "Can't distinguish it from others",
        "Doesn't offer anything new",
        "Won't revolutionize anything",
        "Not innovative",
        "Can't see major advantages",
        "Doesn't improve on existing options",
        "Won't change your life",
        "Not a game changer",
        "Can't justify premium price",
        "Doesn't seem worth splurging on",
        "Won't save you much money either",
        "Not a bargain but not overpriced",
        "Can't say if it's worth it",
        "Doesn't feel like a steal",
        "Won't break the bank",
        "Not cheap but not expensive",
        "Can't decide on value",
        "Doesn't seem particularly good or bad",
        "Won't make much difference",
        "Not a significant upgrade",
        "Can't notice major improvements",
        "Doesn't change much",
        "Won't alter your routine",
        "Not transformative",
        "Can't see dramatic results",
        "Doesn't provide noticeable benefits",
        "Won't solve all problems",
        "Not a complete solution",
        "Can't rely on it entirely",
        "Doesn't cover everything",
        "Won't handle all situations",
        "Not versatile enough",
        "Can't use for multiple purposes",
        "Doesn't adapt well",
        "Won't suit everyone",
        "Not universal",
        "Can't say it's for all users",
        "Doesn't fit every need",
        "Won't work in all cases",
        "Not broadly applicable",
        "Can't generalize about it",
        "Doesn't apply everywhere",
        "Won't be useful to everyone",
        "Not a one-size-fits-all",
        "Can't recommend universally",
        "Doesn't cater to all preferences",
        "Won't please every taste",
        "Not customizable enough",
        "Can't adjust it much",
        "Doesn't offer many options",
        "Won't provide variety",
        "Not flexible",
        "Can't modify easily",
        "Doesn't allow personalization",
        "Won't adapt to preferences",
        "Not very adjustable",
        "Can't tailor it",
        "Doesn't have configuration options",
        "Won't let you choose much",
        "Not highly configurable",
        "Can't fine-tune it",
        "Doesn't support customization",
        "Won't accommodate individual needs",
        "Not particularly adaptable",
        "Can't change settings easily",
        "Doesn't respond to adjustments",
        "Won't reflect preferences",
        "Not responsive to changes",
        "Can't make it personal",
        "Doesn't feel customized",
        "Won't match exactly",
        "Not a perfect fit",
        "Can't align perfectly",
        "Doesn't suit ideally",
        "Won't be exactly right",
        "Not precisely what I wanted",
        "Can't say it's perfect",
        "Doesn't meet all criteria",
        "Won't check every box",
        "Not comprehensive",
        "Can't cover all bases",
        "Doesn't include everything",
        "Won't have all features",
        "Not fully featured",
        "Can't do everything I need",
    ]

    for text in neutral_negations:
        samples.append((text, "neutral"))
        # Add variations
        samples.append((f"{text}. It's okay", "neutral"))
        samples.append((f"I'd say {text.lower()}", "neutral"))

    # === SUBTLE POSITIVE (200 samples) ===
    # Indirect compliments, understated praise

    subtle_positive = [
        "Could be worse I suppose",
        "I've seen worse",
        "Does what it's supposed to",
        "Gets the job done",
        "Serves its purpose",
        "No complaints so far",
        "Decent enough",
        "Fair quality for the price",
        "Acceptable performance",
        "Meets basic requirements",
        "Good enough for me",
        "Does the trick",
        "Works well enough",
        "Pretty much what I expected",
        "Lives up to the description",
        "As advertised",
        "What you see is what you get",
        "Straightforward product",
        "No surprises here",
        "Standard quality",
        "Average in a good way",
        "Solid middle ground",
        "Reasonable option",
        "Fair choice",
        "Suitable for most uses",
        "Appropriate for the task",
        "Fits the bill",
        "Checks the boxes",
        "Covers the basics",
        "Fulfills requirements",
        "Adequate for daily use",
        "Reliable enough",
        "Consistent performance",
        "Steady results",
        "Dependable so far",
        "Holds up well",
        "Maintaining quality",
        "Still working fine",
        "Hasn't failed yet",
        "Going strong",
        "Better than expected honestly",
        "Pleasantly surprised",
        "Exceeded low expectations",
        "Turned out well",
        "Worked out fine",
        "Happy with the outcome",
        "Satisfied overall",
        "Content with purchase",
        "Glad I bought it",
        "Worth considering",
        "Might be worth trying",
        "Could work for you",
        "Potentially good option",
        "Worth a look",
        "Deserves consideration",
        "Has merit",
        "Shows promise",
        "Fairly impressive",
        "Rather good actually",
        "Quite nice",
        "Pretty decent",
        "Somewhat impressive",
        "Moderately good",
        "Relatively solid",
        "Reasonably well-made",
        "Fairly durable",
        "Quite functional",
        "Pretty reliable",
        "Relatively affordable",
        "Reasonably priced",
        "Fair cost",
        "Worth the money arguably",
        "Good value potentially",
        "Decent bang for buck",
        "Fair deal overall",
        "Reasonable investment",
        "Acceptable price point",
        "Not overpriced at least",
        "Priced fairly",
        "Cost seems right",
        "Value is there",
        "Money well spent arguably",
        "Investment justified",
        "Purchase validated",
        "Buying decision confirmed",
        "Choice affirmed",
        "Selection approved",
        "Decision supported",
        "Preference confirmed",
        "Option validated",
        "Pick justified",
        "Growing on me",
        "Warming up to it",
        "Appreciating it more",
        "Liking it better now",
        "Improving with use",
        "Getting better",
        "Increasing satisfaction",
        "More impressed over time",
    ]

    for text in subtle_positive:
        samples.append((text, "positive"))

    # === SUBTLE NEGATIVE (200 samples) ===
    # Indirect criticism, understated complaints

    subtle_negative = [
        "Expected better honestly",
        "Thought it would be nicer",
        "Hoped for more",
        "Could be better",
        "Room for improvement",
        "Leaves something to be desired",
        "Falls a bit short",
        "Missing the mark slightly",
        "Doesn't quite cut it",
        "Just barely acceptable",
        "Borderline disappointing",
        "On the edge of inadequate",
        "Almost good enough",
        "Nearly satisfactory",
        "Close but not quite",
        "Getting there but not yet",
        "Approaching adequate",
        "Somewhat lacking",
        "A bit underwhelming",
        "Slightly disappointing",
        "Mildly frustrating",
        "Moderately annoying",
        "Fairly problematic",
        "Rather concerning",
        "Quite questionable",
        "Pretty mediocre",
        "Notably flawed",
        "Clearly imperfect",
        "Obviously lacking",
        "Evidently inferior",
        "Apparently substandard",
        "Seemingly poor quality",
        "Looks cheaply made",
        "Feels flimsy",
        "Seems fragile",
        "Appears weak",
        "Sounds hollow",
        "Smells like plastic",
        "Looks worse in person",
        "Photos were misleading",
        "Description was generous",
        "Reviews were too kind",
        "Rating seems inflated",
        "Hype was unwarranted",
        "Expectations not met",
        "Promise not delivered",
        "Claims not accurate",
        "Features exaggerated",
        "Benefits overstated",
        "Quality misrepresented",
        "Value questionable",
        "Price seems high",
        "Cost not justified",
        "Expense hard to defend",
        "Money could be better spent",
        "Investment questionable",
        "Purchase regretted somewhat",
        "Buyer's remorse setting in",
        "Second thoughts emerging",
        "Doubts increasing",
        "Concerns growing",
        "Issues multiplying",
        "Problems appearing",
        "Flaws becoming apparent",
        "Defects showing up",
        "Weaknesses revealed",
        "Limitations obvious",
        "Shortcomings evident",
        "Drawbacks clear",
        "Downsides apparent",
        "Negatives outweigh positives",
        "Cons exceed pros",
        "Disadvantages numerous",
        "Problems plentiful",
        "Issues abundant",
        "Complaints valid",
        "Criticisms justified",
        "Feedback negative",
        "Response poor",
        "Service lacking",
        "Support inadequate",
        "Help insufficient",
        "Assistance minimal",
        "Guidance absent",
        "Instructions unclear",
        "Directions confusing",
        "Manual unhelpful",
        "Documentation poor",
        "Information lacking",
        "Details missing",
        "Specifications vague",
        "Description incomplete",
        "Breakdown insufficient",
        "Explanation needed",
        "Clarification required",
        "Understanding difficult",
    ]

    for text in subtle_negative:
        samples.append((text, "negative"))

    # === COMPARATIVE STATEMENTS (300 samples) ===

    # Positive comparisons
    positive_comparisons = [
        "Better than the alternative",
        "Outperforms the competition",
        "Superior to similar products",
        "Beats other options",
        "Exceeds industry standards",
        "Above average quality",
        "Higher tier than expected",
        "Upgraded from my old one",
        "Improvement over previous version",
        "Step up from competitors",
        "Leagues ahead of others",
        "Best in its class",
        "Top of the line",
        "Premium compared to alternatives",
        "Elite level performance",
        "Professional grade unlike others",
        "Commercial quality at home price",
        "Rivals expensive brands",
        "Competes with luxury options",
        "Matches high-end models",
        "Comparable to premium versions",
        "On par with top brands",
        "Equals pricier alternatives",
        "Similar to expensive options",
        "Resembles luxury products",
        "Better value than competitors",
        "More affordable yet better",
        "Cheaper but higher quality",
        "Budget price premium quality",
        "Economical without sacrificing quality",
        "Inexpensive yet reliable",
        "Low cost high performance",
        "Bargain that delivers",
        "Deal that impresses",
        "Steal of a price",
        "Best bang for buck available",
        "Unbeatable value proposition",
        "More features than alternatives",
        "Additional benefits over others",
        "Extra functionality compared",
        "Bonus features included",
        "Enhanced options versus competitors",
        "Improved design over others",
        "Better engineering than similar",
        "Advanced technology compared",
        "Modern approach unlike others",
        "Innovative compared to alternatives",
        "Unique features others lack",
    ]

    for text in positive_comparisons:
        samples.append((text, "positive"))

    # Negative comparisons
    negative_comparisons = [
        "Worse than expected",
        "Inferior to alternatives",
        "Below standard options",
        "Underperforms compared to others",
        "Falls short of competitors",
        "Doesn't measure up",
        "Pales in comparison",
        "Lacking versus alternatives",
        "Deficient compared to similar",
        "Inadequate next to competitors",
        "Subpar relative to others",
        "Lesser quality than alternatives",
        "Downgrade from previous",
        "Step down in quality",
        "Regression from older version",
        "Backward from what I had",
        "Worse than my old one",
        "Previous was better",
        "Used to be good",
        "Quality has declined",
        "Not as good as before",
        "Deteriorated over time",
        "Dropped in quality",
        "Slipped below standards",
        "Fallen from grace",
        "Lost its edge",
        "No longer competitive",
        "Behind the times",
        "Outdated compared to new options",
        "Old technology versus modern",
        "Antiquated approach",
        "Obsolete features",
        "Dated design",
        "Retro not in a good way",
        "Overpriced for what it is",
        "Too expensive compared",
        "Costs more delivers less",
        "Premium price average product",
        "Expensive but disappointing",
        "High cost low value",
        "Pricey yet inferior",
        "Costly with fewer features",
        "Charges more offers less",
        "Not worth the premium",
        "Better options for less money",
        "Cheaper alternatives exist",
        "More affordable competitors available",
        "Budget options are better",
        "Discount brands outperform this",
        "Generic versions superior",
    ]

    for text in negative_comparisons:
        samples.append((text, "negative"))

    return samples

def main():
    print("=" * 70)
    print("ADDING NEGATION & EDGE CASE TRAINING DATA")
    print("=" * 70)
    print("\nThis will improve model performance on:")
    print("  • Negations ('not bad' → positive)")
    print("  • Subtle expressions")
    print("  • Comparative statements")
    print("  • Edge cases")

    # Generate samples
    print("\n📊 Generating specialized samples...")
    training_data = generate_negation_samples()

    # Count by sentiment
    sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
    for _, label in training_data:
        sentiment_counts[label] += 1

    print(f"\n✅ Generated {len(training_data):,} specialized samples")
    print(f"\n📈 Distribution:")
    print(f"   Positive: {sentiment_counts['positive']:,} ({sentiment_counts['positive']/len(training_data)*100:.1f}%)")
    print(f"   Negative: {sentiment_counts['negative']:,} ({sentiment_counts['negative']/len(training_data)*100:.1f}%)")
    print(f"   Neutral:  {sentiment_counts['neutral']:,} ({sentiment_counts['neutral']/len(training_data)*100:.1f}%)")

    # Add to database
    db = SessionLocal()
    try:
        existing_count = db.query(TrainingData).count()
        print(f"\n💾 Current database: {existing_count:,} samples")

        print("\n⏳ Adding specialized samples...")
        added = 0
        skipped = 0

        for idx, (text, label) in enumerate(training_data, 1):
            # Check for duplicates
            existing = db.query(TrainingData).filter(TrainingData.text == text).first()
            if existing:
                skipped += 1
                continue

            # Add new sample
            training_item = TrainingData(
                text=text,
                label=SentimentLabelEnum(label),
                source="negation_edge_cases",
                used_in_training=False
            )
            db.add(training_item)
            added += 1

            # Batch commits
            if idx % 500 == 0:
                db.commit()
                print(f"   Progress: {idx:,}/{len(training_data):,}...")

        db.commit()

        new_total = db.query(TrainingData).count()

        print(f"\n✅ Added {added:,} new samples")
        print(f"   (Skipped {skipped:,} duplicates)")
        print(f"\n🎯 NEW TOTAL: {new_total:,} samples")

        print("\n" + "=" * 70)
        print("NEXT STEP: Retrain the Model")
        print("=" * 70)
        print("\nRun: run_train.bat")
        print("\nThe retrained model will handle:")
        print("  ✓ 'This is not bad' → positive")
        print("  ✓ 'Not impressed' → negative")
        print("  ✓ 'Could be worse' → neutral/positive")
        print("  ✓ 'Better than expected' → positive")
        print("  ✓ Subtle and nuanced language")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
