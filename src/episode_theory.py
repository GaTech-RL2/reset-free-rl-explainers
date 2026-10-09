from schema import chapter as C, episode
P='https://proceedings.mlr.press/v202/nguyen23b.html'
EPISODE=episode('no-regret',5,'No-regret theory','What can reset-free learning guarantee?',
 'Provable Reset-free Reinforcement Learning by No-Regret Reduction',
 'Hoai-An Nguyen, Ching-An Cheng','ICML 2023',P,'#ffab91',
 'Build a constrained MDP, derive the primal–dual regret reduction, and distinguish sublinear expected resets from a zero-reset or finite-reset guarantee.',
 [dict(title='Nguyen & Cheng · ICML 2023',url=P),dict(title='Full paper and proofs',url='https://proceedings.mlr.press/v202/nguyen23b/nguyen23b.pdf')], [
C('What should a reset-free theorem promise?','sublinear',[
 ('Good reward alone is insufficient',r'{\rm Regret}(K)','A learner might use many interventions.'),
 ('Few resets alone is insufficient',r'{\rm Resets}(K)','A learner might simply avoid useful work.'),
 ('Control both as experience grows',r'{\rm Regret}(K),\;{\rm Resets}(K)=o(K)','Both average quantities vanish.')],'''
An agent that never moves may avoid resets while learning almost nothing. An agent that repeatedly crashes and gets restored may learn a rewarding policy while relying on extensive intervention. A meaningful theoretical objective should rule out both shortcuts. Nguyen and Cheng study performance regret and reset cost together, asking whether both can grow sublinearly with the number of learning episodes.

Sublinear growth means that the total divided by the number of episodes tends to zero. A square-root curve is the familiar example: it grows forever, but more slowly than a straight line. Its average rate falls toward zero. This is already an important distinction from a promise of zero resets during training or a finite last reset after which assistance is never needed again.

The paper's contribution is a reduction. It turns reset-free learning into a two-player online optimization problem. If the players achieve suitable no-regret guarantees, the learning system inherits bounds on both performance and resets. We will derive the bridge, identify the assumptions making it possible, and use a small payoff example to understand the role of the reset penalty.
''','Nguyen & Cheng §§3–4; original distinction among total, average, and eventual resets.'),
C('Episodes without routine physical resets','boundaries',[
 ('Use finite-horizon learning rounds',r'h=1,\ldots,H','An episode is a mathematical accounting unit.'),
 ('Carry the physical state into the next round',r's_1^{k+1}\leftarrow s_H^k','Schematic: physical state continues, phase index restarts.'),
 ('A reset state triggers intervention',r's_h\in{\cal S}_{\rm reset}','At most one counted reset in a round.')],'''
The theorem uses finite-horizon episodes, but it does not assume that the environment is freely restored to a fixed start after every episode. If no reset event occurs, the physical state carries into the next round while the episode's time index restarts. Consequently, the initial state of each round depends on what the learner did before. This adaptive sequence is central to the problem.

The environment has designated reset states. Entering one ends the round early and invokes the reset mechanism. The formulation counts at most one such event in an episode. After intervention, the next starting state can again depend on the interaction history. Do not confuse these counted external resets with a learned backward controller physically moving through ordinary states.

This modeling choice is precise and useful, but it is not the most general continuing average-reward process. It is a finite-horizon framework embedded in ongoing physical interaction. The assumptions and theorem should be read within that framework. In particular, the comparator and cost will be evaluated on the adaptive starts actually encountered, rather than on a freely chosen fixed initial distribution.
''','Nguyen & Cheng §3; physical-state carryover shown schematically, not as an implementation index convention.'),
C('Write the two performance measures','regret',[
 ('Compare against a feasible Markovian policy',r'\mathrm{Regret}(K)=\max_{\pi\in\Delta_0(K)}\sum_{k=1}^K[V_r^\pi(s_1^k)-V_r^{\pi_k}(s_1^k)]','The comparator avoids resets at all relevant starts.'),
 ('Use expected reset-event cost',r'\mathrm{Resets}(K)=\sum_{k=1}^K V_c^{\pi_k}(s_1^k)','Each episode contributes a probability in [0,1].'),
 ('The learner determines which starts arise',r's_1^k\;\text{is adaptive}','The comparison is not to another policy’s entire lifetime.')],'''
For each encountered initial state, compare the learner's expected task return with that of a fixed feasible Markovian comparator policy. Sum those differences across episodes, then choose the best comparator in the set that avoids resets at all relevant starts. This defines performance regret. It is a comparison on the learner's encountered states, not a counterfactual comparison between two completely different lifetime trajectories.

For reset cost, assign a cost when the process reaches a reset state. Because the episode stops at its first such event, its cumulative cost is either zero or one. The cost value is therefore the probability of needing a reset in that episode. Summing those expected costs gives the paper's reset measure, conditional on the relevant starting states and policies.

This expected quantity should not be silently replaced by an exact observed count on every random run. The paper's learning guarantees have their stated probability conditions, while the value-based reset measure already contains an expectation over episode dynamics. Keeping these layers separate prevents a high-probability learning statement from being mistaken for a deterministic assurance that no individual run will experience a failure.
''','Nguyen & Cheng Equations 2–3 and Definition of values; original expectation clarification.'),
C('The feasibility assumption is doing real work','feasibility',[
 ('A common reset-free comparator must exist',r'\Delta_0(K)\ne\varnothing','Assumption 3.1 for every admissible start sequence.'),
 ('One good initial state is not enough',r's_1^1\;\text{feasible}\;\not\Rightarrow\;s_1^k\;\text{feasible}','Learning can change the future starts.'),
 ('Reset rules must expose unusable traps',r'{\cal S}_{\rm bad}\subseteq{\cal S}_{\rm reset}','Do not hide in a useless absorbing state.')],'''
Suppose every action from a certain starting state inevitably causes a reset. No algorithm can achieve a vanishing reset rate if that state appears every round. The paper therefore assumes that a reset-free Markovian policy exists for the relevant sequence of episode starts. This makes the comparison class nonempty and establishes that the requested behavior is possible in the modeled problem.

The assumption is stronger than saying the very first state has a safe action. Unknown dynamics can lead the learner to later starts with different possibilities. The theorem has to handle those starts too. Its feasibility assumption is attached to the sequence encountered under the reset mechanism, not merely to the initial demonstration or a designer's favorite nominal configuration.

The formulation also treats bad absorbing states as reset states, preventing a learner from hiding forever in a useless trap to report low intervention cost. These details matter because they connect the mathematical performance measures to the intended practical question. Without a sensible reset mechanism and meaningful encountered starts, small regret could describe a comparison that says very little about useful autonomous learning.
''','Nguyen & Cheng Assumption 3.1 and discussion following Equations 2–3.'),
C('Turn each round into a constrained MDP','constraint',[
 ('Maximize task value at the current start',r'\max_\pi V_r^\pi(s_1^k)','The reward objective is unchanged.'),
 ('Require zero expected reset cost',r'V_c^\pi(s_1^k)=0','The cost is nonnegative.'),
 ('Penalize cost with a multiplier function',r'L_k(\pi,\lambda)=V_r^\pi(s_1^k)-\lambda(s_1^k)V_c^\pi(s_1^k)','Different starts can need different multipliers.')],'''
For a fixed episode start, write a constrained decision problem: maximize task return subject to zero expected reset cost. Since reset costs are nonnegative, zero expected cost means no reset event under the feasible policy in that modeled episode. The challenge is learning such behavior with unknown dynamics while the initial state changes adaptively from round to round.

Introduce a nonnegative Lagrange multiplier that subtracts a price times reset cost from reward. For one fixed start, a scalar price may suffice. Across changing starts, the paper uses a multiplier function of the initial state. This is a substantive feature of the reduction. Different starts can have different reward-versus-reset tradeoffs, so one universal penalty is not the object used in the theorem.

The resulting Lagrangian is a payoff between a policy player and a penalty player. The policy player tries to maximize reward after the reset charge. The penalty player tries to minimize that same payoff. Larger penalties make reset-prone policies less attractive. We can understand this interaction with a two-choice example before dealing with the shared saddle point required across the sequence of decision problems.
''','Nguyen & Cheng §4.1 and Equation 7; original policy-price interpretation.'),
C('A reset penalty changes which policy wins','payoff',[
 ('Safe choice: moderate reward, no cost',r'L_{\rm safe}=0.5','Illustrative one-round payoff.'),
 ('Risky choice: extra reward and reset probability p',r'L_{\rm risky}=0.5+b-\lambda p','b is its extra expected reward.'),
 ('Indifference occurs at a calculable price',r'\lambda_{\rm cross}=\frac{b}{p}','For p>0; this is a toy, not the full algorithm.')],'''
Consider two abstract policy choices. The safe choice earns expected reward point five and has zero reset cost. The risky choice earns point five plus a bonus b and incurs a reset with probability p. Its penalized payoff is point five plus b minus lambda times p. These are deliberately simple policy-level numbers, not a simulation of the paper's learning algorithm.

The risky choice wins when its bonus exceeds its expected reset charge. Set the payoffs equal and solve: the crossing penalty is b divided by p. With bonus point three and reset probability point two, the crossing is one point five. Below that price, the reward incentive dominates. Above it, the safe choice has the larger Lagrangian payoff.

This picture explains why a dual learner can influence exploration through a changing cost price. It also explains why an arbitrary fixed penalty can be inadequate. If the price bound never reaches the needed range, the risky option stays attractive. In the full theorem, the existence and representability of a suitable multiplier function are mathematical conditions, not details that can be ignored after drawing the two lines.
''','Original two-policy Lagrangian example; values are illustrative, not paper results.'),
C('The unusual shared saddle point','saddle',[
 ('The policy maximizes; the dual minimizes',r'\max_\pi\min_{\lambda\geq0}L_k(\pi,\lambda)','Opposing decisions on the same payoff.'),
 ('One saddle pair works across feasible starts',r'L_k(\pi,\widehat\lambda)\leq L_k(\pi^*,\widehat\lambda)\leq L_k(\pi^*,\lambda)','Theorem 4.1 is the key structural result.'),
 ('Zero-cost constraints remove strict feasibility',r'V_c^\pi\geq0\quad\text{and}\quad V_c^\pi\leq0','A standard strictly negative-cost interior is unavailable.')],'''
For a single constrained problem, saddle-point reasoning is familiar: the policy seeks a high payoff and the penalty seeks a low one. But a sequence of different initial states produces a sequence of constrained problems. In general, their best policies and multipliers need not coincide. A reduction to one online game would be much less useful without a common comparator.

The paper proves a shared saddle-point result for its particular reset-free formulation. A Markovian policy and a multiplier function work across the feasible initial states. The proof uses the special zero-reset constraint and the feasibility structure. This common pair is what lets the later regret bounds compare all rounds against compatible objects despite the adaptive initial-state sequence.

There is another subtlety. A common shortcut in constrained optimization assumes a strictly feasible point. Here reset cost is nonnegative and the constraint demands zero, so a strictly negative cost is impossible. The paper establishes the needed result without relying on that shortcut. The existence of the shared saddle point is a theorem to justify, not a generic fact about every constrained reinforcement-learning problem.
''','Nguyen & Cheng Theorem 4.1 and §4.1 discussion of strong duality without Slater’s condition.'),
C('Define regret for each player','primaldual',[
 ('Primal regret compares policies',r'R_p(\pi_c)=\sum_k[L_k(\pi_c,\lambda_k)-L_k(\pi_k,\lambda_k)]','The policy player maximizes.'),
 ('Dual regret compares penalty functions',r'R_d(\lambda_c)=\sum_k[L_k(\pi_k,\lambda_k)-L_k(\pi_k,\lambda_c)]','The dual player minimizes.'),
 ('Adding cancels the played payoff',r'R_p+R_d=\sum_k[L_k(\pi_c,\lambda_k)-L_k(\pi_k,\lambda_c)]','This cancellation drives the reduction.')],'''
Primal regret asks how much more Lagrangian payoff a fixed comparator policy would have earned against the penalties actually played. Dual regret asks how much less payoff a fixed comparator multiplier would have allowed against the policies actually played. The signs differ because the policy player maximizes and the dual player minimizes. Write the signs carefully before trying to use either bound.

Add the two expressions. The payoff of the actual policy paired with the actual multiplier appears once with a minus sign and once with a plus sign, so it cancels. What remains compares the comparator policy against played penalties with played policies against the comparator penalty. This simple cancellation is the algebraic hinge of the reduction.

No regret means these accumulated disadvantages grow sublinearly for the required comparators. It does not mean every individual round improves, or that each player receives full information about an unknown environment. The policy player still has to explore and learn an online sequence of decision problems. That statistical work is essential when the reduction is instantiated as an actual reinforcement-learning algorithm.
''','Nguyen & Cheng Definition 4.4 and discussion following Theorem 4.5; original cancellation derivation.'),
C('Derive the two guarantees','reduction',[
 ('Use a zero dual comparator for reward',r'\mathrm{Regret}(K)\leq R_p(\pi^*)+R_d(0)','The feasible comparator has zero reset cost.'),
 ('Shift the saddle multiplier by one',r'\lambda^*=\widehat\lambda+1','The extra unit exposes cumulative reset cost.'),
 ('Use that comparator for resets',r'\mathrm{Resets}(K)\leq R_p(\pi^*)+R_d(\lambda^*)','Theorem 4.5 bounds both objectives.')],'''
For the performance bound, choose the feasible shared comparator policy and set the dual comparator to zero. In the cancellation formula, the comparator policy's reset cost vanishes. The played policy's zero-penalty payoff is simply its reward. What remains is precisely the reward comparison we wanted, giving the performance-regret inequality displayed on screen.

For resets, the paper uses a multiplier equal to the shared saddle multiplier plus one. The original saddle inequality says the feasible policy is at least as good as a played policy after charging the original penalty. Adding one extra unit of penalty leaves the played policy's reset cost as an additional nonnegative quantity in the comparator gap.

Summing that relation and applying the same regret cancellation bounds cumulative expected resets by primal regret plus dual regret against the shifted multiplier. This is the core reduction: suitable no-regret learners control both objectives. Notice that the two bounds use different dual comparators. Dropping that detail would obscure why one inequality measures reward and the other measures intervention cost.
''','Nguyen & Cheng Corollary 4.3 and Theorem 4.5; original proof walkthrough.'),
C('What the linear-MDP bound assumes','sublinear',[
 ('Known features represent dynamics and signals',r'\phi(s,a)\in\mathbb{R}^{d}','Assumption 5.1: linear MDP structure.'),
 ('Known features represent a bounded dual optimum',r'\lambda^*(s)=\langle\xi(s),\theta^*\rangle,\quad\|\theta^*\|\leq B','Assumption 5.2 includes an appropriate convex set.'),
 ('Both quantities receive the stated rate',r'\widetilde O\!\left((B+1)\sqrt{d^3H^4K}\right)','High-probability result under all stated assumptions.')],'''
The abstract reduction still needs concrete players. The paper instantiates them in a linear MDP setting, using known features that represent transition dynamics, rewards, and reset costs through unknown parameters. It also assumes a known feature representation and bounded convex parameter set for a suitable optimal multiplier function. These are structural assumptions about the problem class, not properties of every neural robot learner.

The policy side uses optimistic value estimates to handle unknown dynamics, and the dual side uses projected gradient updates. Under the stated feasibility and linearity assumptions, the theorem bounds both performance regret and expected reset cost by a rate proportional to B plus one times the square root of d cubed, H to the fourth, and K, up to logarithmic factors.

With dimension, horizon, and multiplier bound fixed, this is square-root growth in the number of episodes. Dividing by K gives a rate that decreases like one over square root K. The constants and structural assumptions remain relevant. This is not a theorem that arbitrary deep RL will eventually operate without intervention, nor a claim that total resets stop growing after a finite training time.
''','Nguyen & Cheng Assumptions 5.1–5.2 and Theorem 5.3; rate transcribed from the primary paper.'),
C('Experiment with prices and rates','payoff',[
 ('Run the declared two-choice toy',r'\pi_k=\arg\max_{\pi\in\{\rm safe,risky\}}L(\pi,\lambda_k)','Exact best response with known payoffs.'),
 ('Update the price by projected descent',r'\lambda_{k+1}=\Pi_{[0,L]}(\lambda_k+\eta c_k)','The plus sign follows from minimizing -lambda c.'),
 ('Compare totals with average rates',r'\sqrt K\uparrow,\quad\frac{\sqrt K}{K}\downarrow','Illustrative scaling, not fitted empirical curves.')],'''
In the theory laboratory, set the risky bonus and reset probability, then run the two-choice price game. The policy uses an exact best response to the current price. The dual update increases the price by learning rate times expected reset cost, then projects onto a declared interval. Because the payoff contains minus lambda times cost, gradient descent on the dual payoff produces this plus sign.

The display plots the price trajectory and reports accumulated expected reset cost. It does not sample crashes, learn unknown dynamics, or implement the paper's optimistic linear-MDP algorithm. This deliberately small experiment isolates how a penalty can change the preferred policy. Lower the price cap below the crossing value and observe why the risky choice can remain attractive indefinitely.

A separate curve shows square-root growth and its corresponding average. Those lines illustrate asymptotic scaling only; they are not numerical theorem bounds with hidden constants or measured benchmark results. Watch the total continue rising while the average falls. That one picture is the most useful antidote to interpreting sublinear resets as a guarantee that there will eventually be no more resets at all.
''','Original payoff lab and scaling illustration; not an implementation or empirical validation of the full theorem.'),
C('A guarantee is an assumption-to-conclusion chain','roadmap',[
 ('Feasibility makes the objective possible',r'\Delta_0(K)\ne\varnothing','A reset-free comparator exists.'),
 ('A shared saddle point enables the reduction',r'R_p,R_d\longrightarrow\mathrm{Regret},\mathrm{Resets}','The comparators are compatible across starts.'),
 ('Statistical structure supplies concrete rates',r'\text{linear MDP assumptions}\longrightarrow\widetilde O(\sqrt K)','The scope travels with the result.')],'''
The theory lesson is a chain. First, define meaningful reward and reset costs on the encountered initial states. Next, assume a feasible reset-free comparator exists. Then prove a common saddle-point structure across those starts. Finally, use primal and dual regret bounds to control both performance and interventions. A concrete linear-MDP algorithm supplies one way to satisfy the reduction's learning requirements.

Each link answers a different question. Feasibility says the desired behavior is possible. The saddle-point theorem says the sequence of constrained problems has compatible reference solutions. The regret reduction translates online optimization performance into reinforcement-learning performance. The linear assumptions make a particular statistical rate available. Removing a link requires a new argument, not simply reusing the final square-root expression.

Our final paper returns to a practical learning mechanism: world models. Instead of proving that a specific linear representation yields a reset bound, MoReFree learns a predictive model and uses imagined trajectories to train goal-reaching behavior. The challenge will be deciding what to practice in imagination and where to collect real data, while the physical world remains stubbornly unresettable.
''','Original synthesis of Nguyen & Cheng; transition to MoReFree.')])
