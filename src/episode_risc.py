from schema import chapter as C, episode
P='https://arxiv.org/abs/2405.01684'
EPISODE=episode('risc',4,'RISC','Switch when the goal becomes easy',
 'Intelligent Switching in Reset-Free RL',
 'Darshan Patil, Janarthanan Rajendran, Glen Berseth, Sarath Chandar','ICLR 2024',P,'#f4cc78',
 'Separate behavior switching from value termination, derive the discounted success critic, and inspect the switching hazard and trajectory-length distribution.',
 [dict(title='RISC · primary paper',url=P),dict(title='Authors’ implementation',url='https://github.com/chandar-lab/RISC')], [
C('Why finish an already-mastered segment?','corridor',[
 ('A fixed schedule spends time everywhere',r'\pi(\cdot\mid s,g_f)\leftrightarrow\pi(\cdot\mid s,g_b)','Both directions contain easy segments.'),
 ('Competence can identify redundant practice',r'F^\pi(s,g)\in[0,1]','A discounted goal-reaching score.'),
 ('Switch early when the current goal is easy',r'F^\pi(s,g)\uparrow\Rightarrow p_{\rm switch}\uparrow','This is a curriculum decision.')],'''
Picture a robot moving between two ends of a corridor. Near either end, reaching that nearby goal has become routine. The interesting learning happens around obstacles in the middle. A fixed schedule keeps sending the robot all the way through mastered segments before turning around. Those extra interactions may add little new information about the parts of the task it still struggles with.

RISC proposes an unusual stopping rule: switch away from the current goal when the agent is confident it can reach it. The goal need not have been physically reached yet. This can shift practice toward less familiar state-goal combinations. It is a curriculum mechanism for allocating experience, rather than a failure detector that activates whenever progress looks poor.

Compare this carefully with Leave no Trace. There, low predicted recovery value rejects a potentially troublesome action. Here, high competence on the current goal increases the chance of handing off to another goal. The two scores answer different questions. This lesson first fixes the value semantics at a handoff, then derives the competence score and the controls that prevent excessive switching.
''','RISC §§4.1–4.2; original corridor explanation and comparison with Leave no Trace.'),
C('Behavior changes; the evaluated goal need not','handoff',[
 ('Collect an action for goal g',r'a\sim\pi(\cdot\mid s,g)','Store the goal with the transition.'),
 ('A scheduler may choose a new behavior goal',r'g_{\rm behavior}^{+}\ne g','The next action can use another goal.'),
 ('Still evaluate continuation for g',r'y_g=r_g+\gamma V(s^\prime,g)','Off-policy target for the original objective.')],'''
At a handoff, the behavior controller changes which goal it pursues. But what should happen to the critic for the old goal? If that critic estimates the return of continuing toward the old goal, its future has not vanished. The successor state still exists, and an imagined continuation of the old policy can still have value from that state.

Off-policy learning separates the policy collecting transitions from the policy being evaluated or improved. A goal-conditioned critic can therefore bootstrap using the original goal even if the next real action is collected for a different goal. The update must use an appropriate off-policy method and goal-consistent reward. We are not claiming that an arbitrary on-policy trajectory can be relabeled without correction.

The important modeling choice is the return being estimated. If you intentionally define a hierarchical option whose return ends at handoff, that is a different objective and may have a different target. RISC's argument concerns critics for the underlying goal-conditioned control task. Treating the scheduler's handoff as their terminal event changes those critics into something the method did not intend to learn.
''','RISC §4.1; original distinction between goal-conditioned continuation and an explicitly terminating option.'),
C('False termination couples the critic to the scheduler','bellman',[
 ('Consistent continuation target',r'y_n=r+\gamma V(s^\prime,g)','Collector boundaries do not remove the tail.'),
 ('A scheduler-dependent target',r'y_t=r+\gamma(1-d_{\rm switch})V(s^\prime,g)','The mask changes when scheduling changes.'),
 ('Changing the scheduler changes the fixed point',r'\mathbb{E}[d_{\rm switch}\mid s,g]','Identical task dynamics can receive different labels.')],'''
Suppose the successor value is eight, reward is zero, and gamma is point nine. The continuation target is seven point two. If a scheduler happens to switch goals at that transition and we label it terminal, the target becomes zero. Nothing about the goal-reaching dynamics changed. Only the behavior schedule changed, yet the critic receives a radically different learning signal.

Now let the scheduler improve over training. It starts switching earlier in familiar regions. Under the false-terminal convention, those very regions receive more zeroed continuation targets. The critic's meaning drifts with the switching policy. In a forward-backward system, the distribution of states also depends on both controllers, making this coupling more complicated than a fixed time limit in an ordinary episodic benchmark.

RISC uses timeout-nonterminal bootstrapping at these handoffs to preserve the continuation targets. True goal success can still terminate the success return under its own definition. The distinction is between a boundary in behavior collection and a boundary in the modeled task. The companion target calculator lets you change the switching decision while holding reward, successor state, and goal constant.
''','RISC §4.1 Equations 4–5; original numerical counterexample.'),
C('Define a competence score','discountreach',[
 ('Count transitions to the current goal',r'\tau_g=\min\{n\geq1:s_n\in g\}','A first-hit time after an action.'),
 ('Use discounted first-success return',r'Q_F=\mathbb{E}[\gamma_{sc}^{\tau_g-1}\mathbf{1}\{\tau_g<\infty\}]','Matches the next-state success-reward convention.'),
 ('Average over the current policy action',r'F^\pi(s,g)=\mathbb{E}_{a\sim\pi}[Q_F(s,a,g)]','Fast reliable success gives a high score.')],'''
RISC needs a measure of how well the current policy can achieve its goal. A useful choice rewards first success and discounts delay. The sooner the goal is reached, the larger the score. Failure to ever reach it contributes zero. This naturally combines ability and distance in one value-like quantity that can be learned with familiar temporal difference machinery.

There is a small indexing convention worth making explicit. In the implemented recurrence, success on the very next transition receives reward one without discount. If tau counts transitions until success, the corresponding return is gamma to tau minus one. The paper also describes the intuition using gamma to a hitting-time index. A one-step shift in the index is bookkeeping, not a different curriculum principle.

For stochastic trajectories, the learned critic estimates an expectation over possible outcomes, rather than the shortest path over all imaginable actions. A policy that sometimes succeeds quickly and sometimes fails can share a score with a slower, more reliable policy. The score is therefore a discounted competence measure. It is not automatically a calibrated probability of eventual success, as the paper explicitly emphasizes.
''','RISC §4.2.1 Equations 6–7; explicit next-state reward indexing and stochastic interpretation.'),
C('Derive the success-critic target','successcritic',[
 ('Detect goal success at the successor',r'f(s^\prime,g)\in\{0,1\}','Success for the current goal.'),
 ('Stop this return at first success',r'y_F=f+(1-f)\gamma_{sc}\widehat Q_F(s^\prime,a^\prime,g)','Success gives one; otherwise continue.'),
 ('Ignore artificial handoffs in this mask',r'a^\prime\sim\pi(\cdot\mid s^\prime,g)','Use the same evaluated goal.')],'''
Let f be a function that tells us whether the successor state satisfies the current goal. If it does, the first-success return is one and there is no additional tail. If it does not, the score is gamma times the estimated continuation under the same goal-conditioned policy. Combining those two cases gives the target on screen.

This recurrence explains why the score stays between zero and one in the ideal setting. The success branch is exactly one. The other branch discounts an existing score in that range. Starting with bounded values, the true fixed point respects the same bounds. A neural approximation can still produce poorly calibrated estimates unless its representation and training handle that constraint appropriately.

The success critic is trained alongside the ordinary task critic using the agent's experience. It requires a success function for the relevant task and reset goals. It does not infer those goal specifications from nothing. At a collector handoff, bootstrap the unsatisfied current goal; at actual first success, use the success branch. Two different boundaries again receive different treatment because they have different meanings.
''','RISC Equation 7 and §4.2.1; original boundedness explanation.'),
C('A score is not yet a good switching rule','hazard',[
 ('Naively switch with constant probability c',r'p_{\rm switch}=c','This is a per-step hazard.'),
 ('The waiting time can be very short',r'\mathbb{E}[T]=\frac1c','For independent constant-hazard trials.'),
 ('Both directions can become trapped in chatter',r'g_f\leftrightarrow g_b\leftrightarrow g_f','Frequent handoffs can prevent exploration.')],'''
Suppose we directly use a competence score of point one as the probability of switching at every step. That number may sound small. But with independent trials and a constant hazard, the expected waiting time is only ten steps. If both directions have moderately high scores in the same region, the robot can keep turning around there instead of reaching unfamiliar territory.

This is a useful distinction between a per-step probability and a trajectory-level probability. Ten percent per step does not mean only ten percent of trajectories switch. Over many opportunities, the chance of at least one switch becomes large. The product of the probabilities of not switching determines how much of the trajectory survives to a given time.

RISC therefore adds three controls rather than feeding the score directly into an unrestricted coin flip. It chooses only a portion of trajectories for early switching, enforces a minimum trajectory length, and gradually relaxes an initially conservative factor. These controls preserve sustained behavior long enough to move through the state space. We will derive their joint effect instead of hiding them inside a single hyperparameter.
''','RISC §4.2.2; original geometric waiting-time derivation.'),
C('The exact early-switching mechanism','hazard',[
 ('Choose eligibility once per trajectory',r'z\sim\mathrm{Bernoulli}(\zeta)','A trajectory-level coin flip.'),
 ('Wait for the minimum length',r't<m\;\Rightarrow\;p_t=0','Except actual goal success or the maximum cutoff.'),
 ('Then use the conservative hazard',r'p_t=F^\pi(s_t,g)(1-\beta^t)','For eligible trajectories with t at least m.')],'''
At the beginning of a trajectory, draw one eligibility coin with probability zeta. If that coin fails, do not perform intelligent early-switch checks during that trajectory. This is not the same as independently multiplying the hazard by zeta at every step. An eligible trajectory keeps its eligibility, and an ineligible one keeps the opportunity to travel farther.

For an eligible trajectory, wait until its length reaches the minimum m. After that, multiply the competence score by one minus beta raised to the current trajectory length. With beta near one, this factor starts small and grows gradually. With beta equal to one exactly, the factor remains zero; the often-stated limit toward the competence score requires beta strictly below one.

Actual goal success triggers a switch, and a maximum length M also forces a handoff. These conditions come before the optional early-switch check in the paper's algorithm. The ordinary task critic still bootstraps through a mere scheduler cutoff. The rule controls which behavior collects data; it does not redefine the goal-reaching task every time the eligibility coin is drawn.
''','RISC Algorithm 2 and §4.2.2; explicit beta=1 boundary case.'),
C('From a hazard to a trajectory distribution','survival',[
 ('Survive all earlier switch opportunities',r'S(t)=\prod_{u=m}^{t}(1-p_u)','Conditional on eligibility and no goal hit.'),
 ('Mix eligible and ineligible trajectories',r'S_{\rm mix}(t)=(1-\zeta)+\zeta S(t)','Before the forced maximum cutoff.'),
 ('Recover an expected length',r'\mathbb{E}[L]=\sum_{t=0}^{M-1}\Pr(L>t)','Our lab uses a fixed competence toy model.')],'''
The switching probability is a hazard: the probability of ending this segment now, conditional on having continued until now. To survive several steps, the segment must avoid every earlier switch. Multiply the one-minus-hazard factors to obtain the survival curve. If the competence score changes along the path, use the score at each corresponding state rather than a single constant.

Now include trajectory eligibility. Before the maximum cutoff, an ineligible trajectory survives every intelligent-switch opportunity. An eligible trajectory survives according to the product. The unconditional survival probability is therefore one minus zeta, plus zeta times the eligible survival curve. This mixture is why replacing the trajectory coin with a per-step factor produces a different length distribution.

Summing the tail probabilities gives expected segment length. The laboratory evaluates this finite sum exactly for a fixed competence, a chosen minimum length, and a forced maximum. It deliberately excludes early physical goal hits so that the switching mechanism can be isolated. You can see how beta, zeta, and the minimum length affect both the mean duration and the chance of long segments.
''','Original survival analysis of RISC Algorithm 2; fixed competence and no-goal-hit toy assumptions.'),
C('The curriculum changes what gets practiced','corridor',[
 ('High competence raises switching likelihood',r'F^\pi(s,g)\uparrow','Spend less time finishing easy segments.'),
 ('A new goal changes the state-goal pair',r'(s,g_f)\longrightarrow(s,g_b)','The physical state does not jump.'),
 ('Data distribution and value semantics are separate',r'\xi_{\rm data}\ne\text{Bellman target definition}','Keep the target stable while coverage changes.')],'''
Return to the corridor picture. As a robot approaches a goal it already knows how to reach, the success critic rises. The scheduler may switch to the opposite goal before arrival. The physical state is unchanged, but the state-goal pair is new. Repeating this mechanism can reallocate experience away from routinely completed tails and toward portions of the problem that remain useful to learn.

The intended result is a curriculum that depends on competence, rather than only on a clock or distance threshold. But competence itself is learned, and the induced data distribution changes as both policy and critic change. A misleading success critic can schedule poor practice. Frequent handoffs can also produce coverage problems despite correct Bellman targets, which is why the modulation mechanisms matter.

Think of target correctness and data usefulness as two separate requirements. Correct bootstrapping gives the critic a consistent quantity to estimate. Intelligent switching tries to improve the examples available for estimating it and improving the policy. Fixing either requirement alone does not automatically solve the other. This separation makes the paper's two major contributions easier to understand and evaluate independently.
''','RISC §§4–5; original distinction between target semantics and coverage.'),
C('Inspect the two ablation questions','comparison',[
 ('What if handoffs zero the value tail?',r'y=r+\gamma(1-d_{\rm switch})V','Tests target consistency.'),
 ('What if switching uses only fixed timeouts?',r't\geq M','Tests the competence curriculum.'),
 ('What if modulation is removed?',r'p_t=F^\pi(s_t,g)','Tests excessive switching and coverage.')],'''
An ablation should isolate a question. Removing timeout-aware bootstrapping tests whether the target's meaning matters. Removing intelligent switching while retaining consistent targets tests whether the learned schedule improves experience allocation. Removing the eligibility coin, minimum length, or conservative factor tests whether the raw competence signal causes excessive switching. These changes are related, but they are not interchangeable explanations.

The paper studies these components empirically in its chosen environments. Our laboratory does not reproduce those learning curves. It exposes the mechanics that make the ablations meaningful. You can compare correct and false-terminal targets without training a neural network, and compare segment-length distributions without changing the physical task. Those controlled examples help explain what the empirical experiments are testing.

When applying the idea elsewhere, examine goal definitions, success detection, and reset feasibility. A high score on an easy but irrelevant goal does not necessarily create useful exploration after switching. Likewise, a controller that cannot reach the alternate goal may accumulate unhelpful data. RISC supplies a scheduling mechanism whose success depends on the surrounding goal-conditioned learning problem.
''','RISC §5.3 and Appendix ablations; original experimental interpretation.'),
C('Use the switching laboratory','survival',[
 ('Set competence, beta, zeta, and m',r'c,\beta,\zeta,m','The maximum length is shown explicitly.'),
 ('Inspect exact expected duration',r'\mathbb{E}[L]=\sum_t S_{\rm mix}(t)','No Monte Carlo noise in the displayed result.'),
 ('Compare scheduler masks on one transition',r'y_n-y_t=\gamma V(s^\prime,g)','At a handoff that is not genuine termination.')],'''
Start with early-switch eligibility equal to zero. Every segment in the toy model reaches the maximum length, because we have excluded goal hits. Increase eligibility while keeping competence fixed. A second population of shorter segments appears in the survival curve. The long tail from ineligible trajectories remains visible until the forced cutoff, exactly as predicted by the mixture equation.

Next increase beta toward one. Switching becomes more conservative early in the trajectory. Increase the minimum length and watch the survival curve stay flat for longer before declining. Finally raise competence. Once checks become active, a more competent agent tends to switch sooner. These effects follow from the actual probability rule, not from a hand-drawn animation.

Below the plot, the target comparison holds the task transition constant. Triggering a handoff changes the false-terminal target but leaves the continuation target alone. This pairs the two lessons in one view: scheduling changes the duration of collected segments, while correct value learning keeps the underlying objective consistent. The physical control problem and the collection schedule are allowed to evolve on different terms.
''','Original exact finite-horizon hazard lab based on RISC Algorithm 2.'),
C('Switching is a learning decision','roadmap',[
 ('Evaluate competence for the current goal',r'F^\pi(s,g)','Discounted first-success return.'),
 ('Modulate the per-step switching hazard',r'p_t=c_t(1-\beta^t)','Use trajectory eligibility and length bounds.'),
 ('Next: bound the total cost of learning',r'{\rm Regret}(K),\quad{\rm Resets}(K)','Move from a mechanism to a theorem.')],'''
RISC reframes a controller handoff as a decision about useful experience. The success critic estimates competence on the current goal. The scheduler uses that estimate to avoid spending every trajectory on already-mastered tails. Its three modulation mechanisms keep the decision from collapsing into rapid back-and-forth switching that explores very little.

The mathematical foundation is just as important as the scheduler. A handoff changes behavior, but need not end the goal-conditioned return being learned. Preserving that distinction keeps the critic's target from drifting with the scheduling rule. We derived both the success target and the trajectory survival curve so that each part of the mechanism can be inspected independently.

The next lesson asks for a different kind of result. Rather than proposing a practical switching heuristic and measuring its performance, can we prove that an agent both learns a good policy and needs progressively fewer resets per unit of experience? The answer will involve a constrained decision process, two no-regret players, and assumptions that are essential to the guarantee.
''','Original synthesis; transition to Nguyen & Cheng.')])
