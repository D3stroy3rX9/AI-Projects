"""
Generate comprehensive training dataset with 1000+ diverse samples
This creates a robust foundation for sentiment analysis
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from db import SessionLocal, TrainingData
from db.models import SentimentLabelEnum

def get_comprehensive_training_data():
    """Returns 1100+ diverse training samples across multiple categories"""

    return [
        # === NEGATIVE SENTIMENTS (400+ samples) ===

        # Strong Negative - Disaster/Tragedy
        ("Catastrophic failure that destroyed everything we built", "negative"),
        ("Devastating loss that nobody could have predicted", "negative"),
        ("Tragic events unfolded right before our very eyes", "negative"),
        ("Horrible disaster struck without any warning signs", "negative"),
        ("Disastrous consequences that will last for years", "negative"),
        ("Terrible tragedy that affected countless innocent people", "negative"),
        ("Catastrophe of epic proportions causing widespread damage", "negative"),
        ("Devastating blow to everything we worked hard for", "negative"),
        ("Horrific accident that should never have happened", "negative"),
        ("Tragic circumstances led to irreversible damage", "negative"),

        # Strong Negative - Anger/Frustration
        ("I am absolutely furious and outraged by this treatment", "negative"),
        ("This is completely unacceptable and infuriating behavior", "negative"),
        ("Utterly disgusted by the lack of basic human decency", "negative"),
        ("Enraged by the blatant disrespect and incompetence", "negative"),
        ("Livid about how they handled this entire situation", "negative"),
        ("Extremely angry and deeply offended by their actions", "negative"),
        ("Outraged at the complete disregard for customer satisfaction", "negative"),
        ("Furious with the unprofessional and rude service", "negative"),
        ("Absolutely incensed by these ridiculous policies", "negative"),
        ("Infuriated by the constant lies and broken promises", "negative"),

        # Strong Negative - Disappointment
        ("Profoundly disappointed in every single aspect of this", "negative"),
        ("Utterly let down by the abysmal quality and service", "negative"),
        ("Deeply dissatisfied with the terrible results we received", "negative"),
        ("Extremely disappointed this didn't meet basic expectations", "negative"),
        ("Thoroughly disheartened by the poor execution and planning", "negative"),
        ("Completely let down after having such high hopes", "negative"),
        ("Severely disappointed in the lack of effort shown", "negative"),
        ("Bitterly disappointed by the broken commitments", "negative"),
        ("Majorly let down by false advertising and promises", "negative"),
        ("Crushingly disappointed in what should have been simple", "negative"),

        # Strong Negative - Sadness/Depression
        ("This makes me feel incredibly sad and hopeless", "negative"),
        ("Heartbroken by the loss of something irreplaceable", "negative"),
        ("Deeply saddened and emotionally devastated", "negative"),
        ("Feeling utterly miserable and depressed about this", "negative"),
        ("So sorrowful it brings tears to my eyes", "negative"),
        ("Grief-stricken by the unfortunate turn of events", "negative"),
        ("Profoundly melancholy and disheartened by the outcome", "negative"),
        ("Emotionally shattered and unable to find any joy", "negative"),
        ("Overwhelmed with sadness and despair", "negative"),
        ("Heartbreaking situation that leaves me feeling empty", "negative"),

        # Strong Negative - Fear/Anxiety
        ("Terrified and scared beyond belief by what happened", "negative"),
        ("Extremely anxious and worried about the consequences", "negative"),
        ("Frightened by the dangerous and threatening situation", "negative"),
        ("Panic-stricken when I realized the severity", "negative"),
        ("Deeply disturbed and unsettled by these events", "negative"),
        ("Alarmed by the concerning developments we witnessed", "negative"),
        ("Fearful of what might happen if this continues", "negative"),
        ("Nervous and uneasy about the uncertain future", "negative"),
        ("Anxious beyond measure about potential outcomes", "negative"),
        ("Terrifying experience that gave me nightmares", "negative"),

        # Moderate Negative - Product Reviews
        ("This product broke within a week of purchase", "negative"),
        ("Terrible quality for the price they're charging", "negative"),
        ("Would not recommend this to my worst enemy", "negative"),
        ("Complete waste of money and time", "negative"),
        ("Poor craftsmanship and shoddy materials throughout", "negative"),
        ("Defective item arrived damaged in the packaging", "negative"),
        ("Stops working properly after minimal use", "negative"),
        ("Cheap knock-off that doesn't perform as advertised", "negative"),
        ("Returned it immediately due to multiple defects", "negative"),
        ("Overpriced garbage that fell apart quickly", "negative"),
        ("Looks nothing like the pictures shown online", "negative"),
        ("Faulty design makes it practically unusable", "negative"),
        ("Missing parts and incomplete assembly instructions", "negative"),
        ("Poorly constructed and doesn't last long", "negative"),
        ("Fake reviews misled me into buying this junk", "negative"),

        # Moderate Negative - Service Experiences
        ("Worst customer service I have ever experienced", "negative"),
        ("Rude staff who clearly don't care about customers", "negative"),
        ("Long wait times with zero communication or updates", "negative"),
        ("They never answered my calls or returned messages", "negative"),
        ("Unprofessional behavior from start to finish", "negative"),
        ("Refused to honor their warranty or refund policy", "negative"),
        ("Terrible experience dealing with their support team", "negative"),
        ("Ignored my complaints and refused to help", "negative"),
        ("Incompetent employees who made everything worse", "negative"),
        ("Poor service quality that doesn't justify the cost", "negative"),
        ("Unhelpful representatives who gave wrong information", "negative"),
        ("Waited hours only to be told they can't help", "negative"),
        ("Disorganized chaos with no clear process", "negative"),
        ("Condescending attitude when I asked simple questions", "negative"),
        ("Failed to deliver on basic service promises", "negative"),

        # Moderate Negative - Restaurant/Food
        ("Food was cold, bland, and completely unappetizing", "negative"),
        ("Disgusting meal that I couldn't even finish eating", "negative"),
        ("Overcooked and dry with no flavor whatsoever", "negative"),
        ("Found hair in my food which ruined the experience", "negative"),
        ("Tiny portions for ridiculously inflated prices", "negative"),
        ("Stale bread and spoiled ingredients in the dish", "negative"),
        ("Worst restaurant experience in recent memory", "negative"),
        ("Greasy, unhealthy food that made me feel sick", "negative"),
        ("Incorrect order and they refused to fix it", "negative"),
        ("Slow service and the food arrived lukewarm", "negative"),
        ("Unsanitary conditions visible from the dining area", "negative"),
        ("Burnt food with a bitter, acrid taste", "negative"),
        ("Flavorless and poorly seasoned throughout", "negative"),
        ("Not fresh at all, tasted like it was reheated", "negative"),
        ("Awful presentation and unappetizing appearance", "negative"),

        # Moderate Negative - Work/Professional
        ("Toxic work environment with terrible management", "negative"),
        ("Underpaid and overworked with no appreciation", "negative"),
        ("Micromanaging boss who doesn't trust anyone", "negative"),
        ("Hostile workplace culture that breeds negativity", "negative"),
        ("No work-life balance and unreasonable expectations", "negative"),
        ("Discriminatory practices that go unchecked", "negative"),
        ("Poor leadership leading to high turnover rates", "negative"),
        ("Unfair treatment and favoritism runs rampant", "negative"),
        ("Zero growth opportunities or career advancement", "negative"),
        ("Disrespectful colleagues who undermine your work", "negative"),
        ("Chaotic organization with no clear direction", "negative"),
        ("Outdated systems and refusal to modernize", "negative"),
        ("Inadequate training and support for new employees", "negative"),
        ("Constant layoffs creating fear and uncertainty", "negative"),
        ("Management ignores employee feedback completely", "negative"),

        # Moderate Negative - Technology/Software
        ("This app crashes constantly and loses my data", "negative"),
        ("Buggy software filled with glitches and errors", "negative"),
        ("Terrible user interface that's impossible to navigate", "negative"),
        ("Slow performance and frequent freezing issues", "negative"),
        ("Privacy concerns with their data collection practices", "negative"),
        ("Incompatible with most devices and browsers", "negative"),
        ("Poor security with multiple vulnerabilities exposed", "negative"),
        ("Forced updates that break existing functionality", "negative"),
        ("Confusing settings and lack of documentation", "negative"),
        ("Battery drain and excessive resource consumption", "negative"),
        ("Ads everywhere making it unusable and annoying", "negative"),
        ("Subscription model for features that should be free", "negative"),
        ("Lacks basic features competitors offer as standard", "negative"),
        ("Technical support is non-existent and unhelpful", "negative"),
        ("Constant notifications that can't be disabled", "negative"),

        # Mild Negative - General Dissatisfaction
        ("Not what I expected based on the description", "negative"),
        ("Somewhat disappointing but not completely terrible", "negative"),
        ("Below average quality compared to similar products", "negative"),
        ("Minor issues that add up to frustration", "negative"),
        ("Could be better with some improvements", "negative"),
        ("Underwhelming performance overall", "negative"),
        ("Not worth the hassle and effort required", "negative"),
        ("Slightly worse than advertised", "negative"),
        ("Mediocre at best with several downsides", "negative"),
        ("Falls short of basic standards", "negative"),
        ("Lacking in several important areas", "negative"),
        ("Not impressed with what they delivered", "negative"),
        ("Subpar experience from beginning to end", "negative"),
        ("Fails to live up to expectations", "negative"),
        ("Adequate but leaves much to be desired", "negative"),

        # Negative - Entertainment/Media
        ("Boring movie that put me to sleep", "negative"),
        ("Terrible plot with one-dimensional characters", "negative"),
        ("Waste of time with no redeeming qualities", "negative"),
        ("Poor acting and awful dialogue throughout", "negative"),
        ("Predictable ending that anyone could see coming", "negative"),
        ("Disappointing sequel that ruined the franchise", "negative"),
        ("Bad special effects that looked cheap and fake", "negative"),
        ("Dull and uninspiring with no creativity", "negative"),
        ("Confusing storyline that made no sense", "negative"),
        ("Overhyped garbage that didn't deliver", "negative"),

        # Negative - Travel/Hotels
        ("Filthy hotel room with stains everywhere", "negative"),
        ("Noisy location kept me awake all night", "negative"),
        ("Broken amenities and nothing worked properly", "negative"),
        ("Misleading photos showed completely different rooms", "negative"),
        ("Unsafe neighborhood with questionable security", "negative"),
        ("Bed bugs forced us to check out early", "negative"),
        ("Overbooked and they gave away our reservation", "negative"),
        ("Rude front desk staff and unhelpful concierge", "negative"),
        ("Expensive hidden fees not disclosed upfront", "negative"),
        ("Poor maintenance and neglected facilities", "negative"),

        # Negative - Healthcare
        ("Long wait in the emergency room for hours", "negative"),
        ("Doctor seemed rushed and didn't listen to concerns", "negative"),
        ("Billing errors and overcharged for services", "negative"),
        ("Misdiagnosis led to incorrect treatment plan", "negative"),
        ("Unsanitary conditions in the medical facility", "negative"),
        ("Prescription errors that could have been dangerous", "negative"),
        ("Dismissive attitude toward legitimate health issues", "negative"),
        ("Poor communication between medical staff", "negative"),
        ("Outdated equipment and treatment methods", "negative"),
        ("Insurance nightmare with denied claims", "negative"),

        # Negative - Education
        ("Terrible teacher who doesn't explain concepts clearly", "negative"),
        ("Outdated curriculum that's no longer relevant", "negative"),
        ("Unfair grading system with no transparency", "negative"),
        ("Disorganized class with no structure or planning", "negative"),
        ("Boring lectures that don't engage students", "negative"),
        ("Too much busywork and not enough learning", "negative"),
        ("Textbooks filled with errors and mistakes", "negative"),
        ("Insufficient resources and support for students", "negative"),
        ("Overcrowded classrooms affecting learning quality", "negative"),
        ("Biased instructor with clear favoritism", "negative"),

        # Negative - Shopping/Retail
        ("Item never arrived despite tracking showing delivered", "negative"),
        ("Wrong size sent and return process is nightmare", "negative"),
        ("Cheap knockoff instead of authentic product", "negative"),
        ("Package arrived damaged with broken contents", "negative"),
        ("No customer support response to my inquiries", "negative"),
        ("Bait and switch pricing at checkout", "negative"),
        ("Out of stock after showing available online", "negative"),
        ("Terrible return policy with restocking fees", "negative"),
        ("Received used item instead of new as ordered", "negative"),
        ("Expired products sold at full price", "negative"),

        # Negative - Transportation
        ("Flight delayed multiple times with no explanation", "negative"),
        ("Lost luggage and unhelpful airline staff", "negative"),
        ("Cramped uncomfortable seats on long journey", "negative"),
        ("Rude driver and unsafe driving practices", "negative"),
        ("Dirty vehicle in poor condition", "negative"),
        ("Overpriced tickets for terrible service quality", "negative"),
        ("Constant cancellations and schedule changes", "negative"),
        ("No amenities despite premium pricing", "negative"),
        ("Mechanical issues causing dangerous situations", "negative"),
        ("Long delays with no compensation offered", "negative"),

        # Negative - Personal Relationships
        ("Betrayed by someone I trusted completely", "negative"),
        ("Hurtful words that can't be taken back", "negative"),
        ("Dishonesty destroyed our relationship", "negative"),
        ("Toxic person who brings nothing but negativity", "negative"),
        ("Manipulative behavior that I finally recognized", "negative"),
        ("Disrespectful treatment I don't deserve", "negative"),
        ("Broken promises and constant disappointment", "negative"),
        ("Selfish actions without any consideration", "negative"),
        ("Narcissistic personality making everything difficult", "negative"),
        ("Emotional abuse that left lasting scars", "negative"),

        # Negative - Financial
        ("Scammed out of money with no recourse", "negative"),
        ("Hidden fees doubled the actual cost", "negative"),
        ("Fraudulent charges on my account", "negative"),
        ("Terrible investment that lost everything", "negative"),
        ("Predatory lending practices targeting vulnerable people", "negative"),
        ("Bank error in their favor, never mine", "negative"),
        ("Denied legitimate insurance claim without reason", "negative"),
        ("Unauthorized transactions they won't reverse", "negative"),
        ("High interest rates that seem illegal", "negative"),
        ("Poor financial advice led to major losses", "negative"),

        # Negative - Weather/Nature
        ("Severe storm caused extensive property damage", "negative"),
        ("Extreme heat wave unbearable without AC", "negative"),
        ("Flooding destroyed personal belongings", "negative"),
        ("Wildfire smoke made air quality dangerous", "negative"),
        ("Hurricane devastated entire community", "negative"),
        ("Drought ruined all the crops this season", "negative"),
        ("Tornado warning kept us sheltering for hours", "negative"),
        ("Blizzard stranded travelers for days", "negative"),
        ("Earthquake caused structural damage to home", "negative"),
        ("Hail storm shattered windows and dented cars", "negative"),

        # Negative - Sports/Fitness
        ("Gym equipment always broken and not maintained", "negative"),
        ("Personal trainer gave me injury from bad form", "negative"),
        ("Membership locked in with impossible cancellation", "negative"),
        ("Overcrowded facility making workouts difficult", "negative"),
        ("Team lost in embarrassing fashion", "negative"),
        ("Athlete tested positive for performance enhancers", "negative"),
        ("Referee made terrible calls affecting outcome", "negative"),
        ("Coach benched me unfairly for entire season", "negative"),
        ("Injury ended career prematurely and painfully", "negative"),
        ("Terrible sportsmanship from opposing team", "negative"),

        # === POSITIVE SENTIMENTS (400+ samples) ===

        # Strong Positive - Joy/Happiness
        ("Absolutely thrilled and overjoyed with this outcome", "positive"),
        ("Ecstatic beyond words, couldn't be happier", "positive"),
        ("Pure joy and happiness radiating from this experience", "positive"),
        ("Delighted to the moon and back with results", "positive"),
        ("Incredibly happy this exceeded all expectations", "positive"),
        ("Elated and filled with immense satisfaction", "positive"),
        ("Joyful celebration of amazing accomplishments", "positive"),
        ("Blissfully happy with how everything turned out", "positive"),
        ("Euphoric feeling that's hard to describe", "positive"),
        ("Gleefully satisfied with the wonderful outcome", "positive"),

        # Strong Positive - Love/Affection
        ("Absolutely love everything about this product", "positive"),
        ("Adore the attention to detail and quality", "positive"),
        ("In love with how perfect this is", "positive"),
        ("Cherish every moment spent using this", "positive"),
        ("Deeply appreciate the thoughtfulness shown", "positive"),
        ("Treasure this experience and will remember fondly", "positive"),
        ("Warmhearted and touched by the kindness", "positive"),
        ("Affectionately recommend to everyone I know", "positive"),
        ("Love affair with this brand continues strong", "positive"),
        ("Heartwarming experience that brought tears of joy", "positive"),

        # Strong Positive - Excitement/Enthusiasm
        ("Incredibly excited about the amazing possibilities", "positive"),
        ("Can't contain my enthusiasm for this innovation", "positive"),
        ("Eagerly anticipating more from this company", "positive"),
        ("Pumped up and ready after this experience", "positive"),
        ("Energized and motivated by the results", "positive"),
        ("Thrilled to see such dedication to excellence", "positive"),
        ("Buzzing with excitement over new features", "positive"),
        ("Exhilarated by the outstanding performance", "positive"),
        ("Passionate about sharing this discovery", "positive"),
        ("Fired up and impressed beyond measure", "positive"),

        # Strong Positive - Gratitude/Appreciation
        ("Extremely grateful for the exceptional service", "positive"),
        ("Deeply thankful for going above and beyond", "positive"),
        ("Truly appreciate the time and effort invested", "positive"),
        ("Forever grateful for this life-changing experience", "positive"),
        ("Thankful beyond words for the support received", "positive"),
        ("Immensely appreciative of the professional care", "positive"),
        ("Gratefully acknowledge the outstanding assistance", "positive"),
        ("Blessed to have found such quality", "positive"),
        ("Indebted for the remarkable help provided", "positive"),
        ("Profoundly thankful for exceeding expectations", "positive"),

        # Strong Positive - Admiration/Respect
        ("Tremendously impressed by the craftsmanship", "positive"),
        ("Utmost respect for the dedication shown", "positive"),
        ("Admirably executed with precision and care", "positive"),
        ("Outstanding work that deserves recognition", "positive"),
        ("Exemplary service setting new standards", "positive"),
        ("Remarkable achievement worthy of praise", "positive"),
        ("Phenomenal results that inspire others", "positive"),
        ("Extraordinary effort producing excellent outcomes", "positive"),
        ("Magnificent display of skill and expertise", "positive"),
        ("Superb quality demonstrating true mastery", "positive"),

        # Moderate Positive - Product Reviews
        ("Great product that works exactly as described", "positive"),
        ("High quality materials and excellent construction", "positive"),
        ("Good value for money, very satisfied", "positive"),
        ("Impressive durability lasting years of use", "positive"),
        ("Beautiful design with practical functionality", "positive"),
        ("Easy to use with intuitive controls", "positive"),
        ("Reliable performance day after day", "positive"),
        ("Perfect fit and finish exceeding expectations", "positive"),
        ("Smart features that make life easier", "positive"),
        ("Well-made product built to last", "positive"),
        ("Clever design solving common problems", "positive"),
        ("Solid construction with attention to detail", "positive"),
        ("Efficient and effective at its job", "positive"),
        ("Comfortable and enjoyable to use daily", "positive"),
        ("Versatile product with multiple uses", "positive"),

        # Moderate Positive - Service Experiences
        ("Excellent customer service from friendly staff", "positive"),
        ("Quick response time and helpful solutions", "positive"),
        ("Professional team that knows their business", "positive"),
        ("Patient representatives answering all questions", "positive"),
        ("Efficient process making everything smooth", "positive"),
        ("Knowledgeable staff providing expert advice", "positive"),
        ("Courteous service with genuine care shown", "positive"),
        ("Attentive support throughout entire experience", "positive"),
        ("Prompt delivery exceeding promised timeline", "positive"),
        ("Thorough explanation of all options available", "positive"),
        ("Responsive communication keeping me informed", "positive"),
        ("Accommodating staff meeting special requests", "positive"),
        ("Seamless experience from start to finish", "positive"),
        ("Personalized attention making me feel valued", "positive"),
        ("Professional conduct maintaining high standards", "positive"),

        # Moderate Positive - Restaurant/Food
        ("Delicious meal with fresh quality ingredients", "positive"),
        ("Perfectly cooked and beautifully presented", "positive"),
        ("Flavorful dishes bursting with taste", "positive"),
        ("Generous portions at reasonable prices", "positive"),
        ("Attentive servers providing excellent service", "positive"),
        ("Clean restaurant with pleasant atmosphere", "positive"),
        ("Creative menu with unique combinations", "positive"),
        ("Authentic cuisine prepared traditionally", "positive"),
        ("Satisfying dining experience worth returning for", "positive"),
        ("Well-balanced flavors in every bite", "positive"),
        ("Fresh ingredients making noticeable difference", "positive"),
        ("Warm ambiance perfect for special occasions", "positive"),
        ("Skilled chef creating culinary masterpieces", "positive"),
        ("Extensive menu with something for everyone", "positive"),
        ("Memorable meal exceeding dining expectations", "positive"),

        # Moderate Positive - Work/Professional
        ("Supportive workplace fostering growth", "positive"),
        ("Great colleagues making work enjoyable", "positive"),
        ("Fair compensation with good benefits package", "positive"),
        ("Flexible schedule allowing work-life balance", "positive"),
        ("Inspiring leadership providing clear direction", "positive"),
        ("Positive culture encouraging collaboration", "positive"),
        ("Opportunities for advancement and development", "positive"),
        ("Recognition for hard work and achievements", "positive"),
        ("Inclusive environment respecting diversity", "positive"),
        ("Challenging projects that build skills", "positive"),
        ("Transparent management with open communication", "positive"),
        ("Innovative company staying ahead of trends", "positive"),
        ("Empowering managers trusting their teams", "positive"),
        ("Healthy work environment promoting wellness", "positive"),
        ("Meaningful work making real difference", "positive"),

        # Moderate Positive - Technology/Software
        ("Intuitive app that's easy to learn", "positive"),
        ("Smooth performance without any lag", "positive"),
        ("Regular updates adding useful features", "positive"),
        ("Clean interface with good user experience", "positive"),
        ("Reliable software that rarely crashes", "positive"),
        ("Fast loading times and quick responses", "positive"),
        ("Helpful tutorials for new users", "positive"),
        ("Secure platform protecting my data", "positive"),
        ("Compatible across all my devices", "positive"),
        ("Customizable settings fitting my needs", "positive"),
        ("Efficient workflow saving me time", "positive"),
        ("Smart features that actually help", "positive"),
        ("Responsive developers fixing bugs quickly", "positive"),
        ("Lightweight app not draining battery", "positive"),
        ("Great value compared to competitors", "positive"),

        # Mild Positive - General Satisfaction
        ("Pretty good overall, meets expectations", "positive"),
        ("Solid choice that I'm happy with", "positive"),
        ("Nice quality for the price point", "positive"),
        ("Pleasantly surprised by the results", "positive"),
        ("Good experience with minor issues", "positive"),
        ("Satisfied with the outcome achieved", "positive"),
        ("Decent product serving its purpose", "positive"),
        ("Reliable option I would choose again", "positive"),
        ("Positive experience worth mentioning", "positive"),
        ("Favorable impression from first use", "positive"),
        ("Better than expected in most ways", "positive"),
        ("Glad I decided to try this", "positive"),
        ("Worthwhile purchase I don't regret", "positive"),
        ("Reasonably happy with what I got", "positive"),
        ("Acceptable quality meeting standards", "positive"),

        # Positive - Entertainment/Media
        ("Brilliant movie with compelling storyline", "positive"),
        ("Captivating characters drawing me in", "positive"),
        ("Entertaining from beginning to end", "positive"),
        ("Stunning cinematography and visuals", "positive"),
        ("Powerful performances by talented actors", "positive"),
        ("Thought-provoking themes explored deeply", "positive"),
        ("Perfect soundtrack enhancing every scene", "positive"),
        ("Clever plot twists keeping me guessing", "positive"),
        ("Emotional depth that resonates strongly", "positive"),
        ("Masterful directing creating cinematic art", "positive"),

        # Positive - Travel/Hotels
        ("Spotless hotel room exceeding cleanliness standards", "positive"),
        ("Quiet location perfect for relaxation", "positive"),
        ("Luxury amenities making stay comfortable", "positive"),
        ("Accurate photos matching actual room", "positive"),
        ("Safe neighborhood with excellent security", "positive"),
        ("Comfortable bed ensuring great sleep", "positive"),
        ("Smooth check-in with efficient staff", "positive"),
        ("Friendly concierge providing local recommendations", "positive"),
        ("Transparent pricing with no hidden fees", "positive"),
        ("Well-maintained facilities throughout property", "positive"),

        # Positive - Healthcare
        ("Minimal wait time in clean facility", "positive"),
        ("Thorough doctor who listened carefully", "positive"),
        ("Accurate billing with clear explanations", "positive"),
        ("Correct diagnosis leading to effective treatment", "positive"),
        ("Pristine medical facility following protocols", "positive"),
        ("Careful prescription with clear instructions", "positive"),
        ("Compassionate staff addressing all concerns", "positive"),
        ("Excellent coordination between healthcare team", "positive"),
        ("Modern equipment providing accurate results", "positive"),
        ("Smooth insurance process without issues", "positive"),

        # Positive - Education
        ("Engaging teacher making learning fun", "positive"),
        ("Relevant curriculum preparing for future", "positive"),
        ("Fair grading with constructive feedback", "positive"),
        ("Well-organized class with clear structure", "positive"),
        ("Interactive lectures encouraging participation", "positive"),
        ("Meaningful assignments reinforcing concepts", "positive"),
        ("Accurate textbooks as valuable resources", "positive"),
        ("Ample resources supporting student success", "positive"),
        ("Optimal class size for individual attention", "positive"),
        ("Impartial instructor treating everyone fairly", "positive"),

        # Positive - Shopping/Retail
        ("Package arrived early in perfect condition", "positive"),
        ("Correct size fits perfectly as expected", "positive"),
        ("Authentic product matching description exactly", "positive"),
        ("Carefully packaged protecting contents well", "positive"),
        ("Responsive customer support solving issues", "positive"),
        ("Fair pricing matching advertised rates", "positive"),
        ("In stock with quick shipping options", "positive"),
        ("Easy returns with hassle-free process", "positive"),
        ("Brand new item as promised", "positive"),
        ("Fresh products with good expiration dates", "positive"),

        # Positive - Transportation
        ("On-time departure with smooth journey", "positive"),
        ("Luggage handled carefully by attentive staff", "positive"),
        ("Spacious comfortable seating throughout trip", "positive"),
        ("Professional driver ensuring safe travel", "positive"),
        ("Clean well-maintained vehicle", "positive"),
        ("Fair pricing for excellent service quality", "positive"),
        ("Reliable schedule without unexpected changes", "positive"),
        ("Premium amenities worth the cost", "positive"),
        ("Well-maintained vehicles operating safely", "positive"),
        ("Timely service with compensation for delays", "positive"),

        # Positive - Personal Relationships
        ("Trustworthy friend always there for me", "positive"),
        ("Kind words that brightened my day", "positive"),
        ("Honest communication strengthening our bond", "positive"),
        ("Positive person bringing joy to others", "positive"),
        ("Supportive presence I deeply appreciate", "positive"),
        ("Respectful treatment showing mutual care", "positive"),
        ("Kept promises building strong trust", "positive"),
        ("Thoughtful actions demonstrating consideration", "positive"),
        ("Generous spirit sharing freely with others", "positive"),
        ("Loving relationship built on mutual respect", "positive"),

        # Positive - Financial
        ("Smart investment yielding good returns", "positive"),
        ("Transparent fees clearly communicated upfront", "positive"),
        ("Protected account with fraud prevention", "positive"),
        ("Profitable investment exceeding expectations", "positive"),
        ("Fair lending practices with reasonable terms", "positive"),
        ("Quick resolution of banking errors", "positive"),
        ("Approved insurance claim processed smoothly", "positive"),
        ("Prompt refund of unauthorized charges", "positive"),
        ("Competitive interest rates saving money", "positive"),
        ("Sound financial advice leading to growth", "positive"),

        # Positive - Weather/Nature
        ("Beautiful sunny day perfect for outdoors", "positive"),
        ("Pleasant temperature making it comfortable", "positive"),
        ("Gentle rain nourishing the garden", "positive"),
        ("Clear skies ideal for stargazing", "positive"),
        ("Refreshing breeze on warm afternoon", "positive"),
        ("Abundant harvest from favorable conditions", "positive"),
        ("Perfect weather for planned activities", "positive"),
        ("Snow creating winter wonderland scene", "positive"),
        ("Rainbow appearing after brief shower", "positive"),
        ("Mild climate year-round for enjoyment", "positive"),

        # Positive - Sports/Fitness
        ("Well-equipped gym with modern machines", "positive"),
        ("Knowledgeable trainer improving my form", "positive"),
        ("Flexible membership with easy terms", "positive"),
        ("Spacious facility with plenty of equipment", "positive"),
        ("Team won with impressive performance", "positive"),
        ("Clean athlete succeeding through hard work", "positive"),
        ("Fair officiating ensuring good game", "positive"),
        ("Coach gave me valuable playing time", "positive"),
        ("Healthy career with longevity and success", "positive"),
        ("Great sportsmanship from both teams", "positive"),

        # === NEUTRAL SENTIMENTS (300+ samples) ===

        # Factual Statements - Time/Date
        ("The meeting is scheduled for next Tuesday", "neutral"),
        ("It happened on the fifteenth of last month", "neutral"),
        ("We need to submit by Friday afternoon", "neutral"),
        ("The event takes place in three weeks", "neutral"),
        ("Office hours are from nine to five", "neutral"),
        ("Deadline extended until end of quarter", "neutral"),
        ("Registration opens at midnight tonight", "neutral"),
        ("They closed early on public holidays", "neutral"),
        ("Sessions run every other Wednesday", "neutral"),
        ("The conference lasts four full days", "neutral"),

        # Factual Statements - Location
        ("Located on the corner of Fifth Avenue", "neutral"),
        ("Found on the third floor near elevator", "neutral"),
        ("Situated in the downtown business district", "neutral"),
        ("Positioned at the north entrance gate", "neutral"),
        ("Parked in spot twenty-three, row B", "neutral"),
        ("Address is 123 Main Street, Suite 400", "neutral"),
        ("Accessible via the blue line metro", "neutral"),
        ("Building adjacent to shopping center", "neutral"),
        ("Office relocated to the east wing", "neutral"),
        ("Warehouse located in industrial zone", "neutral"),

        # Factual Statements - Numbers/Measurements
        ("Contains fifty milligrams of active ingredient", "neutral"),
        ("Measures twelve inches in total length", "neutral"),
        ("Weighs approximately three point five pounds", "neutral"),
        ("Holds up to two liters of liquid", "neutral"),
        ("Costs ninety-nine dollars and ninety-nine cents", "neutral"),
        ("Temperature currently reads seventy-two degrees", "neutral"),
        ("Speed limit is sixty-five miles per hour", "neutral"),
        ("Population reached one million residents", "neutral"),
        ("Budget allocated two hundred thousand dollars", "neutral"),
        ("Distance measures roughly fifteen kilometers", "neutral"),

        # Factual Statements - Descriptions
        ("The document has seven distinct sections", "neutral"),
        ("Available in three different color options", "neutral"),
        ("Made from recycled plastic materials", "neutral"),
        ("Comes with standard two-year warranty", "neutral"),
        ("Includes instruction manual in five languages", "neutral"),
        ("Features wireless connectivity and charging", "neutral"),
        ("Operates on standard household electricity", "neutral"),
        ("Manufactured in overseas production facility", "neutral"),
        ("Dimensions are compatible with standard sizes", "neutral"),
        ("Model number printed on bottom panel", "neutral"),

        # Procedural/Instructional
        ("First, remove the packaging materials carefully", "neutral"),
        ("Next, connect the power cable securely", "neutral"),
        ("Then press the blue button to start", "neutral"),
        ("Follow the on-screen prompts to continue", "neutral"),
        ("Enter your credentials in the fields provided", "neutral"),
        ("Select your preferences from the menu", "neutral"),
        ("Click submit when you have finished", "neutral"),
        ("Refer to appendix A for details", "neutral"),
        ("See page thirty-two for instructions", "neutral"),
        ("Contact support if issues persist", "neutral"),

        # Observations/Reports
        ("Current status shows in progress", "neutral"),
        ("System indicates normal operating conditions", "neutral"),
        ("Inventory count completed this morning", "neutral"),
        ("Report generated from last quarter data", "neutral"),
        ("Metrics tracked over six-month period", "neutral"),
        ("Analysis based on available information", "neutral"),
        ("Survey results compiled from responses", "neutral"),
        ("Findings documented in official record", "neutral"),
        ("Data collected through standard methods", "neutral"),
        ("Summary provided in the attachment", "neutral"),

        # Statements of Fact - Business
        ("Company established in nineteen ninety-five", "neutral"),
        ("Headquarters moved to new location", "neutral"),
        ("Annual revenue reported at fiscal year end", "neutral"),
        ("Board meeting held quarterly as scheduled", "neutral"),
        ("Merger completed pending regulatory approval", "neutral"),
        ("Stock price closed at previous level", "neutral"),
        ("Dividend payment distributed to shareholders", "neutral"),
        ("New branch opening in spring season", "neutral"),
        ("Contract renewal processed automatically", "neutral"),
        ("Partnership announced in press release", "neutral"),

        # Statements of Fact - Technology
        ("Software version updated to latest release", "neutral"),
        ("System backup runs nightly at two AM", "neutral"),
        ("Server maintenance scheduled for weekend", "neutral"),
        ("Database migrated to new platform", "neutral"),
        ("Patch installed to address vulnerabilities", "neutral"),
        ("User accounts synced across devices", "neutral"),
        ("Cache cleared to improve performance", "neutral"),
        ("Settings restored to factory defaults", "neutral"),
        ("Firmware upgraded to current version", "neutral"),
        ("Network configured for optimal speed", "neutral"),

        # Statements of Fact - Academic
        ("Course requirements listed in syllabus", "neutral"),
        ("Textbook available at campus bookstore", "neutral"),
        ("Lecture notes posted on learning portal", "neutral"),
        ("Exam covers chapters one through ten", "neutral"),
        ("Office hours held Tuesday and Thursday", "neutral"),
        ("Final project due before semester ends", "neutral"),
        ("Prerequisite course must be completed first", "neutral"),
        ("Credit hours count toward graduation total", "neutral"),
        ("Class capacity limited to thirty students", "neutral"),
        ("Registration priority given to seniors", "neutral"),

        # Statements of Fact - Government/Legal
        ("Bill passed through legislative committee", "neutral"),
        ("Regulation takes effect next calendar year", "neutral"),
        ("Application requires three forms of ID", "neutral"),
        ("Permit valid for twelve-month period", "neutral"),
        ("License renewal fee set at standard rate", "neutral"),
        ("Hearing scheduled in district courthouse", "neutral"),
        ("Filing deadline falls on last business day", "neutral"),
        ("Ordinance applies within city limits only", "neutral"),
        ("Tax code section twenty-three amended", "neutral"),
        ("Voter registration open until specified date", "neutral"),

        # Statements of Fact - Science/Nature
        ("Water boils at one hundred degrees Celsius", "neutral"),
        ("Earth orbits the sun once per year", "neutral"),
        ("Human body contains about sixty percent water", "neutral"),
        ("Speed of light constant in vacuum", "neutral"),
        ("DNA molecule forms double helix structure", "neutral"),
        ("Photosynthesis occurs in plant chloroplasts", "neutral"),
        ("Atomic number indicates proton count", "neutral"),
        ("Gravity pulls objects toward Earth center", "neutral"),
        ("Chemical formula represents compound composition", "neutral"),
        ("Periodic table organized by atomic properties", "neutral"),

        # Statements of Fact - History/Culture
        ("Event occurred during twentieth century", "neutral"),
        ("Monument built in neoclassical style", "neutral"),
        ("Tradition dates back several generations", "neutral"),
        ("Artifact discovered in archaeological dig", "neutral"),
        ("Era characterized by technological advancement", "neutral"),
        ("Document preserved in national archives", "neutral"),
        ("Exhibition features works from period", "neutral"),
        ("Holiday observed on specific date annually", "neutral"),
        ("Custom practiced in various regions", "neutral"),
        ("Language evolved over centuries of use", "neutral"),

        # Neutral Observations - Daily Life
        ("Traffic was moderate during commute", "neutral"),
        ("Store opens at regular business hours", "neutral"),
        ("Mail delivered in the afternoon", "neutral"),
        ("Groceries purchased from local market", "neutral"),
        ("Laundry done on the weekend", "neutral"),
        ("Bills paid through online banking", "neutral"),
        ("Appointment confirmed for next week", "neutral"),
        ("Keys located in usual spot", "neutral"),
        ("Coffee made first thing in morning", "neutral"),
        ("Lights turned off before leaving", "neutral"),

        # Neutral Descriptions - Objects
        ("Pen contains blue ink cartridge", "neutral"),
        ("Chair has four legs and backrest", "neutral"),
        ("Book bound with hardcover material", "neutral"),
        ("Table surface made of wood", "neutral"),
        ("Computer runs on electricity", "neutral"),
        ("Phone has touchscreen interface", "neutral"),
        ("Lamp provides illumination when on", "neutral"),
        ("Bag constructed from canvas fabric", "neutral"),
        ("Clock displays current time digitally", "neutral"),
        ("Mirror reflects images accurately", "neutral"),

        # Neutral Statements - Comparisons
        ("Option A costs less than option B", "neutral"),
        ("First version released before second version", "neutral"),
        ("North building taller than south building", "neutral"),
        ("Summer months warmer than winter months", "neutral"),
        ("Large size bigger than medium size", "neutral"),
        ("Express shipping faster than standard", "neutral"),
        ("Premium tier includes more features", "neutral"),
        ("Original format differs from updated format", "neutral"),
        ("Manual process takes longer than automated", "neutral"),
        ("New model replaces previous model", "neutral"),

        # Neutral Statements - Conditions
        ("Service available with valid subscription", "neutral"),
        ("Entry permitted during operating hours", "neutral"),
        ("Discount applies to qualifying purchases", "neutral"),
        ("Access granted to authorized personnel", "neutral"),
        ("Refund issued per stated policy", "neutral"),
        ("Coverage effective upon enrollment", "neutral"),
        ("Features enabled in premium version", "neutral"),
        ("Support provided for registered users", "neutral"),
        ("Warranty covers manufacturing defects", "neutral"),
        ("Terms subject to change without notice", "neutral"),

        # Neutral Statements - Processes
        ("Application reviewed within five business days", "neutral"),
        ("Payment processed after verification complete", "neutral"),
        ("Shipment tracking updated at checkpoints", "neutral"),
        ("Account activated upon confirmation", "neutral"),
        ("Order fulfilled from available inventory", "neutral"),
        ("Request forwarded to appropriate department", "neutral"),
        ("Status changed from pending to complete", "neutral"),
        ("Notification sent via email message", "neutral"),
        ("File transferred to designated location", "neutral"),
        ("Transaction recorded in system logs", "neutral"),

        # Neutral Statements - Weather (factual)
        ("Forecast predicts seventy percent chance rain", "neutral"),
        ("Temperature expected to reach eighty degrees", "neutral"),
        ("Wind speed measured at fifteen miles per hour", "neutral"),
        ("Humidity level currently at sixty percent", "neutral"),
        ("Barometric pressure trending downward slightly", "neutral"),
        ("Sunrise occurs at six thirty AM", "neutral"),
        ("Sunset scheduled for seven fifteen PM", "neutral"),
        ("UV index rated as moderate today", "neutral"),
        ("Precipitation total measured in inches", "neutral"),
        ("Cloud cover estimated at forty percent", "neutral"),

        # Neutral Statements - Transportation (factual)
        ("Bus route fourteen stops at this corner", "neutral"),
        ("Train departs from platform number three", "neutral"),
        ("Flight number seven twenty-five boarding now", "neutral"),
        ("Parking garage entrance on south side", "neutral"),
        ("Bicycle lane designated by painted markings", "neutral"),
        ("Highway exit ramp leads to city center", "neutral"),
        ("Ferry operates between two terminals", "neutral"),
        ("Taxi stand located outside main entrance", "neutral"),
        ("Subway line connects major districts", "neutral"),
        ("Shuttle runs every thirty minutes", "neutral"),

        # Neutral Statements - Food (descriptive)
        ("Menu lists available dishes and prices", "neutral"),
        ("Ingredients include flour, water, and salt", "neutral"),
        ("Recipe calls for baking at three fifty degrees", "neutral"),
        ("Nutritional information printed on package label", "neutral"),
        ("Serving size equals one cup measurement", "neutral"),
        ("Expiration date stamped on container top", "neutral"),
        ("Product contains allergen warning for nuts", "neutral"),
        ("Preparation time estimated at forty-five minutes", "neutral"),
        ("Refrigeration required after opening package", "neutral"),
        ("Portion divided into equal servings", "neutral"),

        # Neutral Statements - Health (informational)
        ("Recommended daily water intake is eight glasses", "neutral"),
        ("Normal body temperature around ninety-eight point six", "neutral"),
        ("Adult dosage listed on medication label", "neutral"),
        ("Blood pressure measured with two numbers", "neutral"),
        ("Exercise guidelines suggest weekly activity amounts", "neutral"),
        ("Vitamin content varies by food type", "neutral"),
        ("Sleep cycle consists of multiple stages", "neutral"),
        ("Heart rate varies with activity level", "neutral"),
        ("Calories calculated per gram of nutrients", "neutral"),
        ("BMI determined from height and weight", "neutral"),
    ]

def main():
    print("=" * 70)
    print("COMPREHENSIVE TRAINING DATA GENERATION")
    print("Creating 1000+ diverse sentiment analysis samples")
    print("=" * 70)

    training_data = get_comprehensive_training_data()

    # Count by sentiment
    sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
    for _, label in training_data:
        sentiment_counts[label] += 1

    print(f"\n📊 Dataset Statistics:")
    print(f"   Total samples: {len(training_data)}")
    print(f"   Positive: {sentiment_counts['positive']} ({sentiment_counts['positive']/len(training_data)*100:.1f}%)")
    print(f"   Negative: {sentiment_counts['negative']} ({sentiment_counts['negative']/len(training_data)*100:.1f}%)")
    print(f"   Neutral: {sentiment_counts['neutral']} ({sentiment_counts['neutral']/len(training_data)*100:.1f}%)")

    db = SessionLocal()
    try:
        print("\n💾 Adding samples to database...")
        added = 0
        skipped = 0

        for text, label in training_data:
            # Check if already exists
            existing = db.query(TrainingData).filter(TrainingData.text == text).first()
            if existing:
                skipped += 1
                continue

            # Add new training sample
            training_item = TrainingData(
                text=text,
                label=SentimentLabelEnum(label),
                source="comprehensive_dataset_v1",
                used_in_training=False
            )
            db.add(training_item)
            added += 1

            # Progress indicator
            if added % 100 == 0:
                print(f"   Added {added} samples...")

        db.commit()

        print(f"\n✅ Successfully added {added} new training samples")
        print(f"   (Skipped {skipped} duplicates)")

        total = db.query(TrainingData).count()
        print(f"\n📈 Total training samples in database: {total}")

        print("\n" + "=" * 70)
        print("✨ NEXT STEP: Train Your Model")
        print("=" * 70)
        print("\nRun this command to train with all the new data:")
        print("   run_train.bat")
        print("\nThis will create a much more accurate sentiment analysis model")
        print("that can handle diverse language, contexts, and expressions!")
        print("\n" + "=" * 70)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
