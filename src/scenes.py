"""Original geometric teaching scenes. Every plotted number is an explicit toy calculation."""
import math
from drawing import *

def label(c,s):c.text(80,160,s,18,MUTED,True)
def foot(c,s,color=MUTED):c.wrap(95,610,s,875,21,color)

def world(c,p,b,ep):
    label(c,'ONE PHYSICAL TRAJECTORY')
    c.box(96,234,786,266,color=LINE)
    c.box(134,365,118,86,'start',GREEN,size=21);c.box(708,258,124,87,'goal',GOLD,size=21)
    c.box(460,335,105,130,'obstacle',RED,size=17)
    route=[(194,407),(312,438),(373,305),(487,263),(652,288),(767,300),(697,462),(515,509),(340,490),(194,407)]
    x,y=c.path(route,p,CYAN,4);c.circle(x,y,12,CYAN,CYAN)
    for j in range(3):
        xx=140+j*260;c.box(xx,538,225,48,['task actions','recovery actions','human reset'][j],[CYAN,GREEN,RED][j] if b>=j else LINE,size=20)
    foot(c,'A line in the training log does not move the physical state.')

def boundaries(c,p,b,ep):
    label(c,'SAME WORLD · DIFFERENT BOUNDARIES')
    for j in range(3):
        y=258+j*130;c.text(86,y-43,['TRUE TERMINATION','COLLECTOR CUTOFF','CONTROLLER HANDOFF'][j],19,[RED,GOLD,GREEN][j],True)
        c.arrow((120,y),(840,y),LINE,3)
        for k in range(7):c.circle(160+k*100,y,7,CYAN,CYAN)
        cut=560;c.line([(cut,y-28),(cut,y+28)],[RED,GOLD,GREEN][j],4,j==1)
        if j==0:c.text(600,y-35,'tail = 0',23,RED)
        else:
            c.arrow((cut+20,y),(840,y),[GOLD,GREEN][j-1],4)
            c.text(600,y-35,['','keep the tail','new behavior'][j],23,[RED,GOLD,GREEN][j])
        xx=lerp(160,760,p);c.circle(xx,y,11,[RED,GOLD,GREEN][j],BG,3)
    foot(c,'The modeled return determines whether the continuation disappears.')

def bellman(c,p,b,ep):
    label(c,'SPLIT THE RETURN INTO NOW + LATER')
    vals=[1,.9,.81,.729,.656,.590]
    for i,val in enumerate(vals):
        x=122+i*123;h=210*val
        c.box(x,495-h,86,h,f'{val:.2f}',CYAN if i==0 else PURPLE,size=22)
        c.text(x+43,527,f't + {i}',19,MUTED,anchor='mm')
    c.text(165,236,'now',25,CYAN,True,'mm');c.text(587,236,'discounted future',25,PURPLE,True,'mm')
    if b>=1:c.line([(279,245),(872,245)],PURPLE,3)
    if b==2:
        c.box(300,555,536,44,'Do not erase the tail at a handoff',GREEN,size=22)
    foot(c,'Illustration: reward = 1 at each transition; discount = 0.9.')

def valuecurve(c,p,b,ep):
    label(c,'EXACT ONE-STATE FIXED POINTS')
    c.axes(xlabel='false-cutoff probability p',ylabel='value',h=290,y=540)
    c.curve(lambda x:10,ymax=11,h=290,y=540,color=CYAN)
    c.curve(lambda x:1/(1-.9*(1-x)),ymax=11,h=290,y=540,color=RED,p=max(.12,p*1.5))
    pp=.6*ease(p);v=1/(1-.9*(1-pp));x=120+700*pp;y=540-290*v/11
    c.circle(x,y,8,RED,RED);c.line([(x,y),(x,540)],RED,2,True)
    c.text(540,225,'correct: V = 10',23,CYAN)
    c.text(480,455,f'false mask: V = {v:.2f}',23,RED)
    for i in range(6):c.text(120+i*140,562,f'{i/5:.1f}',18,MUTED,anchor='mm')
    foot(c,'Reward 1, discount 0.9. Independent cutoffs are a toy assumption.')

def clockstate(c,p,b,ep):
    label(c,'THE CLOCK CHANGES WHAT THE SAME STATE MEANS')
    for j,remaining in enumerate([10,1]):
        x=145+j*440;c.box(x,233,325,278,color=[GREEN,RED][j]);c.text(x+163,277,f'{remaining} steps remain',26,[GREEN,RED][j],True,'mm')
        c.node(x+66,375,'s',CYAN);c.node(x+170,375,'•',PURPLE);c.node(x+271,375,'g',GOLD)
        c.arrow((x+104,375),(x+130,375),CYAN);c.arrow((x+207,375),(x+232,375),CYAN)
        c.text(x+164,460,['reachable','deadline too soon'][j],25,[GREEN,RED][j],anchor='mm')
    foot(c,'For a genuine finite-horizon task, remaining time belongs in the state.')

def replay(c,p,b,ep):
    label(c,'PRESERVE THE CAUSAL TRANSITION')
    for x,s,co in [(190,'s',CYAN),(510,'actual s′',GREEN),(810,'reset start',RED)]:c.box(x-95,295,190,105,s,co,size=26)
    c.arrow((290,347),(405,347),CYAN,4);c.text(346,288,'action',23,CYAN,anchor='mm')
    c.arrow((612,347),(703,347),RED,3);c.text(659,285,'reset',23,RED,anchor='mm')
    c.box(143,468,452,77,'bootstrap from this successor',GREEN,size=22)
    c.arrow((510,402),(510,461),GREEN)
    c.text(720,499,'separate event',22,RED)
    foot(c,'A wrapper’s fresh-start observation must not replace the actual successor.')

def objectives(c,p,b,ep):
    label(c,'DEPLOYMENT COMPETENCE AND LIFETIME REWARD')
    for j in range(2):
        x=110+j*445;c.box(x,238,365,305,color=[CYAN,GREEN][j])
        c.text(x+182,280,['stay at goal','practice full cycle'][j],25,[CYAN,GREEN][j],True,'mm')
        for k in range(7):
            yy=345+k*23;v=1 if j==0 else (.9 if k%3 else .23)
            c.line([(x+40,yy),(x+40+v*280,yy)],[CYAN,GREEN][j],13)
        c.text(x+182,507,['high ongoing reward','repeated useful starts'][j],20,MUTED,anchor='mm')
    foot(c,'Conceptual comparison: these bars are a toy reward pattern, not benchmark data.')

def histogram(c,p,b,ep,key):
    label(c,'STATE DISTRIBUTIONS · NORMALIZED EIGHT-BIN TOY')
    target=[.05,.09,.16,.23,.23,.14,.07,.03];initial=[.40,.25,.14,.08,.05,.04,.025,.015]
    t=ease(p) if key in ['histogram','jsdivergence','occupancy'] else .25
    q=[lerp(a,z,t) for a,z in zip(initial,target)]
    for i,(a,z) in enumerate(zip(target,q)):
        x=120+i*93
        c.d.rectangle((x,527-a*660,x+29,527),fill=PURPLE)
        c.d.rectangle((x+34,527-z*660,x+63,527),fill=CYAN)
        c.text(x+31,552,str(i+1),19,MUTED,anchor='mm')
    c.text(140,219,'target / demo',24,PURPLE);c.text(480,219,'backward visits',24,CYAN)
    js=sum(.5*(a*math.log(a/((a+z)/2))+z*math.log(z/((a+z)/2))) for a,z in zip(target,q))
    c.text(820,582,f'JS = {js:.4f} nats',22,GOLD,anchor='ra')
    foot(c,'Matching occupancy influences the next starts; the two distributions need not be identical.')

def trap(c,p,b,ep):
    label(c,'REACHABILITY IS A PROPERTY OF THE ACTION GRAPH')
    pts=[(175,370,'start',GREEN),(406,275,'A',CYAN),(700,264,'goal',GOLD),(426,483,'B',CYAN),(750,474,'trap',RED)]
    for a,z in [(0,1),(1,2),(2,0),(0,3),(3,4)]:
        aa=pts[a];zz=pts[z];a2=pos(aa[:2],zz[:2],.19);b2=pos(aa[:2],zz[:2],.81)
        c.arrow(a2,b2,RED if z==4 else GREEN if a==2 else LINE,4)
    for x,y,s,co in pts:c.node(x,y,s,co,43)
    c.text(585,353,'a return path exists',23,GREEN,anchor='mm')
    c.text(687,550,'no outgoing return path',22,RED,anchor='mm')
    route=[pts[0][:2],pts[1][:2],pts[2][:2],pts[0][:2]];x,y=c.path(route,p,CYAN,4);c.circle(x,y,8,CYAN,CYAN)
    foot(c,'A weak policy and a physically irreversible state are different explanations for failure.')

def roadmap(c,p,b,ep):
    label(c,'DECISIONS HIDDEN BY A RESET BUTTON')
    rows=[('RETURN','What does the critic predict?',CYAN),('RECOVERY','Can the agent get back?',GREEN),('DISTRIBUTION','Where should practice begin?',PURPLE),('SCHEDULE','When should behavior switch?',GOLD),('EVIDENCE','What does a theorem or model justify?',BLUE)]
    for j,(tag,s,co) in enumerate(rows):
        y=224+j*75;c.box(100,y,210,53,tag,co,size=19);c.text(335,y+25,s,23,INK,anchor='lm')
    foot(c,'Keep the objective, data distribution, and intervention budget explicit.')

def twopolicies(c,p,b,ep):
    label(c,'TWO CONTROLLERS · ONE CONTINUOUS WORLD')
    c.box(130,250,270,108,'forward policy',CYAN,size=28);c.box(605,250,270,108,'reset policy',GREEN,size=28)
    c.arrow((402,290),(594,290),CYAN,4);c.text(500,250,'handoff',21,MUTED,anchor='mm')
    c.arrow((604,416),(400,416),GREEN,4)
    c.box(330,450,342,96,'physical environment',PURPLE,size=24)
    for x in (267,740):c.arrow((x,359),(x,489),[CYAN,GREEN][x==740],3)
    c.arrow((267,489),(321,489),CYAN);c.arrow((740,489),(681,489),GREEN)
    foot(c,'Different rewards; shared dynamics. A reset policy does not reverse time.')

def actiongate(c,p,b,ep):
    label(c,'SCORE THE PROPOSED ACTION BEFORE EXECUTION')
    c.box(86,304,230,95,'propose a_forward',CYAN,size=21)
    c.box(398,289,250,128,'reset Q(s, a)',GREEN,size=27)
    c.arrow((322,350),(389,350),CYAN,4)
    c.arrow((656,330),(775,271),GREEN,4);c.arrow((656,386),(775,473),RED,4)
    c.box(779,236,167,74,'execute',GREEN,size=22);c.box(779,448,167,74,'handoff',RED,size=22)
    c.text(690,265,'Q ≥ q',23,GREEN);c.text(690,466,'Q < q',23,RED)
    route=[(118,349),(523,349),((860 if b<2 else 860),(273 if b<2 else 485))]
    x,y=c.path(route,p,CYAN,3);c.circle(x,y,9,GOLD,GOLD)
    foot(c,'V(s) can be high while a particular outward action has low recovery value.')

def discountreach(c,p,b,ep):
    label(c,'DISCOUNTED FIRST-SUCCESS RETURN')
    c.axes(xlabel='transitions to first success',ylabel='score (success probability = 1)')
    c.curve(lambda x:.9**(x-1),x0=1,x1=30,color=GREEN,p=min(1,p*1.4))
    for j in range(6):c.text(120+j*140,565,str(1+round(j*29/5)),19,MUTED,anchor='mm')
    c.text(170,239,'next-step success = 1',23,GREEN)
    n=1+int(29*p);score=.9**(n-1);x=120+700*(n-1)/29;y=535-310*score
    c.circle(x,y,9,GOLD,GOLD);c.text(520,429,f'τ = {n}     score = {score:.3f}',24,GOLD)
    foot(c,'Declared convention: one reward at first success, discount 0.9, no later rewards.')

def recovermap(c,p,b,ep):
    label(c,'A LEARNED THRESHOLD CHANGES PERMITTED ACTIONS')
    threshold=.3+.4*ease(p)
    for i in range(20):
        for j in range(10):
            score=max(0,1-(i/20)**1.4-.25*math.sin(j/10*math.pi)**2)
            x=130+i*36;y=223+j*32;co=GREEN if score>=threshold else RED
            c.d.rectangle((x,y,x+32,y+28),fill=blend(BG,co,.16+.55*score))
    c.text(135,570,'reset region',22,GREEN);c.text(620,570,'difficult actions →',22,RED)
    c.text(600,188,f'threshold q = {threshold:.2f}',23,GOLD)
    foot(c,'Analytic landscape slice. Allowed pairs live in state-action space, not just state space.')

def ensemble(c,p,b,ep):
    label(c,'SAME QUERY · THREE CRITIC ESTIMATES')
    estimates=[.2,.5,.8];threshold=.6
    for j,q in enumerate(estimates):
        x=190+j*240;h=330*q;c.box(x,542-h,126,h,f'{q:.1f}',[RED,GOLD,GREEN][j],size=27)
        c.text(x+63,574,f'critic {j+1}',22,MUTED,anchor='mm')
    yy=542-330*threshold;c.line([(130,yy),(886,yy)],PURPLE,3,True);c.text(882,yy-34,'q = 0.6',22,PURPLE,anchor='ra')
    c.text(126,207,['max = 0.8: permit','mean = 0.5: reject','min = 0.2: reject'][b],27,[GREEN,GOLD,RED][b],True)
    foot(c,'Different aggregation rules express different exploration choices; none certifies calibration.')

def attempts(c,p,b,ep):
    label(c,'FAILED RECOVERY ATTEMPTS ARE EVIDENCE, NOT A PROOF')
    n=1+int(p*7)
    for j in range(8):
        x=148+j*99;c.circle(x,337,33,GREEN if j<n else LINE,blend(BG,GREEN,.12) if j<n else BG)
        c.text(x,337,str(j+1),25,INK,anchor='mm')
    c.text(150,423,f'N = {n} attempts, toy success probability = 0.3',25,CYAN)
    c.text(150,478,f'Probability all fail = 0.7^{n} = {.7**n:.3f}',26,GOLD)
    c.box(148,539,664,47,'Real attempts may be correlated and change the state.',LINE,size=20)
    foot(c,'Increasing the budget trades fewer interventions against time spent trying to recover.')

def loop(c,p,b,ep):
    label(c,'A COUPLED LEARNING LOOP')
    names=['collect actions','store transitions','update objectives','choose behavior']
    pts=[(250,276),(729,276),(729,504),(250,504)]
    for j,((x,y),s) in enumerate(zip(pts,names)):
        c.box(x-136,y-42,272,84,s,[CYAN,GREEN,PURPLE,GOLD][j],size=23)
        nxt=pts[(j+1)%4];a=pos((x,y),nxt,.30);z=pos((x,y),nxt,.70);c.arrow(a,z,[CYAN,GREEN,PURPLE,GOLD][j],4)
    x,y=c.path(pts+[pts[0]],p,ep['color'],2);c.circle(x,y,9,ep['color'],ep['color'])
    foot(c,'Track task actions, recovery actions, and external resets separately.')

def curriculum(c,p,b,ep):
    label(c,'USEFUL INTERMEDIATE STARTS CAN EXPOSE SPARSE SUCCESS')
    c.line([(143,380),(865,380)],LINE,8)
    for j in range(8):
        x=150+j*100;c.node(x,380,'g' if j==7 else str(j),GOLD if j==7 else GREEN if j==0 else PURPLE,27)
        if b>=1 and j in [2,4,6]:c.arrow((x,274),(x,333),PURPLE,3)
    c.text(150,443,'original start',22,GREEN,anchor='mm');c.text(850,443,'reward',22,GOLD,anchor='mm')
    c.text(500,240,'demonstration states become practice targets',23,PURPLE,anchor='mm')
    x=lerp(150 if b==0 else 550,850,p);c.circle(x,380,13,CYAN,CYAN)
    c.box(195,518,632,63,'Evaluation still begins from the intended start distribution.',LINE,size=20)
    foot(c,'Illustrative corridor; useful training starts do not redefine the final task.')

def classifier(c,p,b,ep):
    label(c,'CLASSIFICATION WITH AN EXPLICIT LABEL CONVENTION')
    for i in range(15):
        x=146+(i%5)*35;y=262+(i//5)*39;c.circle(x,y,10,PURPLE,PURPLE)
        c.circle(x,y+183,10,CYAN,CYAN)
    c.text(127,211,'demo: label 1',23,PURPLE);c.text(127,561,'backward: label 0',23,CYAN)
    c.arrow((337,300),(461,365),PURPLE);c.arrow((337,482),(461,415),CYAN)
    c.box(470,339,180,121,'C(s)',GOLD,size=37);c.arrow((661,400),(782,400),GOLD)
    c.text(841,348,'0 … 1',32,GOLD,anchor='mm');c.text(820,461,'relative',23,MUTED,anchor='mm');c.text(820,491,'membership',23,MUTED,anchor='mm')
    foot(c,'At the optimum, the output is a density ratio, not a geometric distance.')

def densityratio(c,p,b,ep):
    label(c,'POINTWISE OPTIMUM OF A BINARY CLASSIFIER')
    a=.3;bb=lerp(.4,.1,p);D=a/(a+bb)
    for j,(name,v,co) in enumerate([('demo mass',a,PURPLE),('backward mass',bb,CYAN),('classifier output',D,GOLD)]):
        y=285+j*115;c.text(117,y-38,name,23,co);c.box(117,y,700*v,43,color=co,fill=blend(BG,co,.4));c.text(870,y+22,f'{v:.3f}',25,co,anchor='rm')
    foot(c,'Holding demo mass fixed, lower backward coverage raises the optimal classifier output.')

def logreward(c,p,b,ep):
    label(c,'FROM A DISCRIMINATOR SCORE TO A RESET REWARD')
    c.axes(xlabel='classifier output C',ylabel='reward −log(1 − C)',h=295)
    c.curve(lambda x:-math.log(max(.01,1-x)),x0=0,x1=.99,ymax=4.7,color=PURPLE,p=max(.05,p))
    D=.1+.8*ease(p);r=-math.log(1-D);x=120+700*D/.99;y=535-295*r/4.7
    c.circle(x,y,9,GOLD,GOLD);c.text(178,285,f'C = {D:.2f}',25,GOLD);c.text(178,326,f'reward = {r:.3f}',25,PURPLE)
    c.text(790,562,'0.99',18,MUTED);c.text(120,562,'0',18,MUTED)
    foot(c,'Demo label = 1. The sign changes if the classifier’s label convention changes.')

def comparison(c,p,b,ep):
    label(c,'COMPARE THE MECHANISM AND THE MEASUREMENT')
    rows=[('TASK','final competence','same evaluation starts',CYAN),('DATA','physical interactions','include recovery actions',GREEN),('HELP','outside supervision','count resets and demos',PURPLE),('SCOPE','analytic toy vs. experiment','do not mix the claims',GOLD)]
    for j,(tag,a,z,co) in enumerate(rows):
        y=231+j*91;c.box(95,y,115,59,tag,co,size=19);c.text(237,y+7,a,24,co,True);c.text(237,y+39,z,21,MUTED)
    foot(c,'The companion links primary sources and labels every illustrative numerical model.')

def corridor(c,p,b,ep):
    label(c,'SWITCHING REALLOCATES STATE–GOAL EXPERIENCE')
    c.box(114,269,757,196,color=LINE)
    c.box(122,278,157,178,'easy',GREEN,size=24);c.box(711,278,151,178,'easy',GREEN,size=24)
    c.text(499,314,'still learning',28,GOLD,True,'mm')
    for x,y in [(400,359),(530,402),(603,348)]:c.circle(x,y,21,RED,blend(BG,RED,.3))
    route=[(180,407),(361,438),(475,342),(655,395),(803,398)]
    if b>=1:route=[(316,405),(477,341),(681,394),(491,452),(316,405)]
    x,y=c.path(route,p,CYAN,4);c.circle(x,y,13,CYAN,CYAN)
    c.text(187,514,'reset goal',22,GREEN,anchor='mm');c.text(801,514,'task goal',22,GOLD,anchor='mm')
    foot(c,'Early switching is based on high competence for the current goal, not low recovery value.')

def handoff(c,p,b,ep):
    label(c,'SAME SUCCESSOR · TWO DIFFERENT BEHAVIOR GOALS')
    c.node(206,381,'s',CYAN,47);c.node(498,381,'s′',PURPLE,47);c.arrow((257,381),(443,381),CYAN,4)
    c.arrow((547,355),(777,270),CYAN,4);c.arrow((547,413),(777,496),GREEN,4)
    c.box(769,222,172,96,'old goal',CYAN,size=24);c.box(769,455,172,96,'new goal',GREEN,size=24)
    c.text(307,294,'observed action',22,MUTED,anchor='mm')
    c.text(575,229,'critic continues',23,CYAN);c.text(557,541,'behavior switches',23,GREEN)
    foot(c,'Off-policy learning evaluates the chosen goal even when the next behavior goal differs.')

def successcritic(c,p,b,ep):
    label(c,'TWO CASES DEFINE THE FIRST-SUCCESS TARGET')
    c.box(113,301,216,124,'success at s′?',GOLD,size=24)
    c.arrow((336,330),(539,257),GREEN,4);c.arrow((336,395),(539,487),CYAN,4)
    c.box(548,205,329,101,'yes → target = 1',GREEN,size=25)
    c.box(548,443,329,108,'no → γ × next score',CYAN,size=22)
    c.text(570,346,'stop at first success',21,GREEN);c.text(558,578,'continue through a handoff',21,CYAN)
    foot(c,'The success indicator terminates this return; an artificial switching event does not.')

def hazard(c,p,b,ep):
    label(c,'PER-STEP SWITCH HAZARD · FIXED COMPETENCE TOY')
    c.axes(xlabel='trajectory length t',ylabel='conditional switch probability',h=285)
    c.curve(lambda t:0 if t<15 else .7*(1-.97**t),x0=0,x1=100,color=GOLD,h=285,p=max(.1,p*1.35))
    c.line([(120+700*.15,240),(120+700*.15,535)],PURPLE,2,True)
    c.text(268,282,'minimum m = 15',22,PURPLE);c.text(566,402,'c = 0.7, β = 0.97',22,GOLD)
    for j in range(6):c.text(120+j*140,565,str(j*20),18,MUTED,anchor='mm')
    foot(c,'Early-switch eligibility is sampled once per trajectory; goal hits and max length also switch.')

def survival(c,p,b,ep):
    label(c,'SURVIVAL OF A SEGMENT UNDER INTELLIGENT SWITCHING')
    vals=[1];s=1
    for t in range(1,101):
        if t>=15:s*=1-.12*(1-.97**t)
        vals.append(s)
    c.axes(xlabel='trajectory length t',ylabel='probability segment continues',h=290)
    c.curve(lambda t:vals[min(100,int(t))],x0=0,x1=100,color=GOLD,h=290,p=max(.12,p*1.3))
    c.curve(lambda t:.4+.6*vals[min(100,int(t))],x0=0,x1=100,color=CYAN,h=290,p=max(.12,p*1.3))
    c.text(435,275,'eligible only',23,GOLD);c.text(432,315,'60% eligible mixture',23,CYAN)
    c.text(130,573,'0',18,MUTED);c.text(802,573,'100',18,MUTED)
    foot(c,'No goal hits in this toy. All surviving segments are forced to end at the maximum.')

def sublinear(c,p,b,ep):
    label(c,'SUBLINEAR TOTAL DOES NOT MEAN FINITE TOTAL')
    c.axes(xlabel='number of episodes K',ylabel='illustrative total',h=285)
    c.curve(lambda x:x,x0=0,x1=1,color=RED,h=285,p=max(.08,p*1.4))
    c.curve(lambda x:.40*math.sqrt(x),x0=0,x1=1,color=GREEN,h=285,p=max(.08,p*1.4))
    c.text(595,281,'linear growth',24,RED);c.text(473,440,'square-root growth',24,GREEN)
    c.text(240,575,'Total keeps growing; total / K decreases.',23,GOLD)
    foot(c,'Schematic scaling with arbitrary coefficients. Not fitted data or a numerical theorem bound.')

def regret(c,p,b,ep):
    label(c,'COMPARE BOTH POLICIES ON THE ENCOUNTERED STARTS')
    for j in range(4):
        x=145+j*204;c.node(x,273,f's{j+1}',PURPLE,31)
        c.arrow((x,310),(x,352),MUTED)
        c.box(x-76,365,152,69,'π* feasible',GREEN,size=18);c.box(x-76,476,152,69,'π learner',CYAN,size=18)
    c.text(505,220,'adaptive initial-state sequence',25,PURPLE,anchor='mm')
    foot(c,'The comparator avoids resets for all relevant starts; it is not another lifetime trajectory.')

def feasibility(c,p,b,ep):
    label(c,'A RESET-FREE COMPARATOR MUST EXIST')
    c.node(233,371,'start',CYAN,45);c.node(658,255,'safe',GREEN,45);c.node(658,501,'reset',RED,45)
    c.arrow((278,350),(612,272),GREEN,4);c.arrow((278,398),(612,486),RED,4)
    c.text(454,254,'feasible route',24,GREEN,anchor='mm');c.text(454,514,'reset-prone route',24,RED,anchor='mm')
    if b>=1:c.box(142,558,697,49,'Without a feasible route, no learner can promise a vanishing reset rate.',LINE,size=18)
    foot(c,'The assumption must cover the relevant sequence of starts, not just the first state.')

def constraint(c,p,b,ep):
    label(c,'CONSTRAINED RETURN: REWARD WITH ZERO RESET COST')
    c.axes(xlabel='expected reset cost',ylabel='expected task reward',h=285)
    for i in range(28):
        x=(i%7)/6;y=.2+.65*(.5+.5*math.sin(i*1.9));c.circle(120+x*700,535-y*285,7,RED if x>0 else GREEN,RED if x>0 else GREEN)
    c.line([(120,226),(120,539)],GREEN,5);c.text(160,250,'feasible boundary: cost = 0',24,GREEN)
    foot(c,'Nonnegative cost makes zero cost a boundary constraint: strict negative-cost feasibility is absent.')

def payoff(c,p,b,ep):
    label(c,'AN EXACT TWO-POLICY PAYOFF EXAMPLE')
    c.axes(xlabel='reset penalty λ',ylabel='Lagrangian payoff',h=280)
    c.curve(lambda x:.5,x0=0,x1=4,ymax=1,color=GREEN,h=280)
    c.curve(lambda x:max(0,.8-.2*x),x0=0,x1=4,ymax=1,color=RED,h=280)
    xx=120+700*1.5/4;c.line([(xx,245),(xx,545)],GOLD,2,True)
    c.text(575,321,'safe: 0.5',24,GREEN);c.text(495,468,'risky: 0.8 − 0.2 λ',24,RED)
    c.text(xx,574,'crossing λ = 1.5',23,GOLD,anchor='mm')
    x=lerp(0,3.5,p);v=max(.5,.8-.2*x);c.circle(120+700*x/4,535-280*v,9,CYAN,CYAN)
    foot(c,'Toy payoffs with known rewards and costs. This is not the full linear-MDP learning algorithm.')

def saddle(c,p,b,ep):
    label(c,'ONE COMPATIBLE SADDLE PAIR ACROSS DIFFERENT STARTS')
    for j in range(3):
        x=215+j*290;c.box(x-95,257,190,76,f'CMDP {j+1}',PURPLE,size=24);c.arrow((x,339),(504,458),PURPLE,3)
    c.box(336,460,338,102,'shared (π*, λ̂)',GREEN,size=28)
    c.text(505,211,'different initial states',24,MUTED,anchor='mm')
    foot(c,'A special theorem for this reset-free formulation, not a generic property of all CMDPs.')

def primaldual(c,p,b,ep):
    label(c,'TWO PLAYERS: MAXIMIZE AND MINIMIZE THE SAME PAYOFF')
    c.box(117,294,300,146,'policy player π',CYAN,size=27);c.box(590,294,300,146,'penalty player λ',PURPLE,size=27)
    c.arrow((420,325),(581,325),CYAN,4);c.arrow((585,402),(427,402),PURPLE,4)
    c.text(267,486,'maximize L',25,CYAN,anchor='mm');c.text(739,486,'minimize L',25,PURPLE,anchor='mm')
    c.box(183,543,637,52,'Played payoff cancels when the two regrets are added.',GOLD,size=21)
    foot(c,'The primal learner still has to explore unknown dynamics; cancellation is only the reduction.')

def reduction(c,p,b,ep):
    label(c,'THE SAME CANCELLATION SUPPORTS TWO COMPARATORS')
    c.box(126,234,303,92,'primal regret',CYAN,size=26);c.box(568,234,303,92,'dual regret',PURPLE,size=26)
    c.text(501,280,'+',38,GOLD,anchor='mm');c.arrow((500,340),(500,412),GOLD,4)
    c.box(155,439,687,99,['reward regret: dual comparator 0','reset bound: shifted multiplier','both totals inherit sublinear growth'][b],GREEN,size=24)
    foot(c,'The reset bound uses λ* = λ̂ + 1; that extra unit exposes cumulative reset cost.')

def worldmodel(c,p,b,ep):
    label(c,'REAL EVIDENCE → LEARNED DYNAMICS → IMAGINED PRACTICE')
    c.box(91,307,244,114,'real transitions',CYAN,size=25);c.box(406,307,227,114,'world model',PURPLE,size=25);c.box(710,307,240,114,'policy learning',GREEN,size=24)
    c.arrow((342,363),(397,363),CYAN,4);c.arrow((639,363),(702,363),PURPLE,4)
    for i in range(5):
        pts=[(510,296),(575+i*40,223-i*12),(692+i*42,201+i*8)]
        c.path(pts,clamp(p*1.8-i*.12),PURPLE,2)
    c.line([(826,430),(826,529),(219,529),(219,428)],GREEN,3);c.arrow((219,465),(219,427),GREEN,3)
    c.text(510,565,'improved behavior collects the next evidence',23,GREEN,anchor='mm')
    foot(c,'Model rollouts are computational. Physical recovery still requires real actions.')

def distance(c,p,b,ep):
    label(c,'TEMPORAL SEPARATION SUPERVISES A DYNAMICAL DISTANCE')
    for j in range(8):
        x=140+j*103;c.node(x,340,str(j),CYAN if j<2 or j>6 else PURPLE,25)
        if j<7:c.arrow((x+31,340),(x+71,340),LINE,2)
    c.line([(346,403),(346,439),(758,439),(758,403)],GOLD,3)
    c.text(552,488,'4 actions separate this state pair',26,GOLD,anchor='mm')
    c.text(500,241,'sample states from an imagined trajectory',24,MUTED,anchor='mm')
    foot(c,'A learned action-distance signal depends on the policy, the model, and trajectory coverage.')

def goexplore(c,p,b,ep):
    label(c,'ONE GO-EXPLORE CALL CONTAINS TWO REAL CONTROL PHASES')
    c.box(106,287,389,160,'GO toward selected goal',CYAN,size=24);c.box(517,287,384,160,'EXPLORE from arrival',GOLD,size=24)
    c.arrow((496,367),(515,367),MUTED,4)
    c.text(300,497,'H_G physical actions',23,CYAN,anchor='mm');c.text(709,497,'H_E physical actions',23,GOLD,anchor='mm')
    x=lerp(142,864,p);c.circle(x,558,11,CYAN,CYAN);c.line([(142,558),(864,558)],LINE,2)
    foot(c,'The explore phase begins at the state actually reached, even if the go phase misses its goal.')

def backforth(c,p,b,ep):
    label(c,'TWO REAL ROUTINES SHARE ONE CONTINUOUS TRAJECTORY')
    for j,txt in enumerate(['task goal','explore','initial goal','explore']):
        x=100+j*219;c.box(x,302,197,122,txt,[GOLD,PURPLE,GREEN,PURPLE][j],size=23)
        if j<3:c.arrow((x+199,363),(x+216,363),MUTED,3)
    c.text(311,258,'FORWARD GO-EXPLORE',22,GOLD,anchor='mm');c.text(750,258,'BACK GO-EXPLORE',22,GREEN,anchor='mm')
    c.text(500,502,'selected together with probability α',27,CYAN,anchor='mm')
    c.text(500,553,'otherwise: one exploratory-goal routine',23,MUTED,anchor='mm')
    foot(c,'Sampling an initial-state goal commands a return; it does not guarantee successful recovery.')

def mixture(c,p,b,ep):
    label(c,'GOALS USED FOR IMAGINED POLICY TRAINING')
    alpha=.2 if b==0 else lerp(.2,.8,p);vals=[alpha/2,alpha/2,1-alpha]
    x=133
    for v,co,s in zip(vals,[GOLD,GREEN,PURPLE],['task goals','initial goals','replay goals']):
        w=730*v;c.box(x,310,w,112,color=co,fill=blend(BG,co,.24))
        if w>75:c.text(x+w/2,366,f'{v:.0%}',27,co,True,'mm')
        x+=w
    for j,(v,co,s) in enumerate(zip(vals,[GOLD,GREEN,PURPLE],['task goals','initial goals','replay goals'])):
        c.text(149+j*258,488,s,22,co);c.text(149+j*258,531,f'{v:.1%}',26,co,True)
    c.text(142,236,f'α = {alpha:.2f}   ·   weights sum to 1',25,CYAN)
    foot(c,'These are imagination-goal weights. The real exploration routine uses a different branching schedule.')

def callfraction(c,p,b,ep):
    label(c,'BRANCH PROBABILITY ≠ FRACTION OF GO-EXPLORE CALLS')
    c.axes(xlabel='α',ylabel='fraction',h=290)
    c.curve(lambda x:x,color=PURPLE,h=290)
    c.curve(lambda x:2*x/(1+x),color=GOLD,h=290,p=max(.1,p*1.5))
    c.text(476,270,'2α / (1 + α)',27,GOLD);c.text(590,410,'α',29,PURPLE)
    x=120+700*.2;y=535-290/3;c.circle(x,y,9,GOLD,GOLD);c.text(150,218,'α = 0.2 → 1/3 of calls',23,GOLD)
    foot(c,'Equal call lengths; the paired branch executes two calls while the other branch executes one.')

def modelerror(c,p,b,ep):
    label(c,'ACCUMULATED ERROR IN A DECLARED LINEAR DYNAMICS TOY')
    c.axes(xlabel='rollout step',ylabel='position',h=290)
    c.curve(lambda x:x/1.3,color=CYAN,h=290,p=max(.1,p*1.3))
    c.curve(lambda x:1.2*x/1.3,color=RED,h=290,p=max(.1,p*1.3))
    c.text(450,265,'model gain = 1.2',25,RED);c.text(530,443,'true gain = 1',25,CYAN)
    c.line([(820,535-290/1.3),(820,535-290*1.2/1.3)],GOLD,4)
    c.text(854,284,'gap',22,GOLD)
    foot(c,'Constant action and constant gain bias. Nonlinear closed-loop errors need not grow linearly.')

def scene(c,key,p,b,ep):
    basic={'world':world,'boundaries':boundaries,'bellman':bellman,'valuecurve':valuecurve,'clockstate':clockstate,'replay':replay,'objectives':objectives,'trap':trap,'roadmap':roadmap,'twopolicies':twopolicies,'actiongate':actiongate,'discountreach':discountreach,'recovermap':recovermap,'ensemble':ensemble,'attempts':attempts,'loop':loop,'curriculum':curriculum,'classifier':classifier,'densityratio':densityratio,'logreward':logreward,'comparison':comparison,'corridor':corridor,'handoff':handoff,'successcritic':successcritic,'hazard':hazard,'survival':survival,'sublinear':sublinear,'regret':regret,'feasibility':feasibility,'constraint':constraint,'payoff':payoff,'saddle':saddle,'primaldual':primaldual,'reduction':reduction,'worldmodel':worldmodel,'distance':distance,'goexplore':goexplore,'backforth':backforth,'mixture':mixture,'callfraction':callfraction,'modelerror':modelerror}
    if key in ['occupancy','histogram','jsdivergence']:histogram(c,p,b,ep,key)
    else:basic[key](c,p,b,ep)
