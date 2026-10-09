from schema import chapter as C, episode
P='https://arxiv.org/abs/1711.06782'
EPISODE=episode('leave-no-trace',2,'Leave no Trace','Learn to recover before you explore',
 'Leave no Trace: Learning to Reset for Safe and Autonomous Reinforcement Learning',
 'Benjamin Eysenbach, Shixiang Gu, Julian Ibarz, Sergey Levine','ICLR 2018',P,'#83e0b2',
 'Turn a learned reset value into an action gate. Understand action-conditioned recovery, uncertainty, and why a recoverability score is not a universal safety certificate.',
 [dict(title='Leave no Trace · primary paper',url=P)], [
C('A successful action can ruin the next attempt','trap',[
 ('Both routes can earn task reward',r'r_f(s_{\rm goal})=1','Task reward alone misses recovery.'),
 ('Only one route permits a return',r'\Pr(\tau_{\cal R}<\infty\mid s_{\rm trap})=0','The next attempt needs a path back.'),
 ('Learn a second skill',r'\pi_f(a\mid s),\quad\pi_b(a\mid s)','Forward and backward control.')],'''
Imagine two ways to push a puck into a scoring region. One leaves the puck near the center of the table. The other sends it into a pocket that the robot cannot reach. Both produce the same immediate task reward. For a single trial they look equally good, but for a robot that must keep practicing, one action destroys the next trial.

On the graph, color the task goals gold and the starting region green. One gold node has a path back to green; the other is an absorbing trap. A task critic trained only for reaching gold has no reason to prefer the reversible route. We need a second quantity that asks about the future after the apparent success.

Leave no Trace introduces a learned reset policy alongside the forward policy. The reset policy does more than clean up afterward. Its value function judges proposed forward actions before execution. This turns recovery into a learned constraint on exploration. We will separate the exact action gate from the uncertainty in its estimates, because that uncertainty determines whether the gate is useful.
''','Leave no Trace §§4–5; original puck interpretation of the reversible/absorbing-goal example.'),
C('Two rewards describe two skills','twopolicies',[
 ('Forward behavior maximizes task return',r'J_f=\mathbb{E}_{\pi_f}\!\left[\sum_t\gamma^t r_f(s_t,a_t)\right]','Reach the task objective.'),
 ('Backward behavior maximizes reset return',r'J_b=\mathbb{E}_{\pi_b}\!\left[\sum_t\gamma^t r_b(s_t,a_t)\right]','Return to a useful initial region.'),
 ('Alternate in the same world',r's_{\rm start}^{b}=s_{\rm end}^{f}','The handoff does not teleport.')],'''
Define a forward reward for accomplishing the task and a reset reward for returning to states near the initial distribution. These are two control problems with shared physical dynamics. They may use different rewards, different policies, and different critics. A backward policy is not generally the forward policy with its actions negated; contact, friction, and object geometry make literal time reversal unreliable.

The training loop alternates the two controllers. The forward policy starts from the state actually produced by the preceding reset attempt. The reset policy starts from the state actually produced by the forward attempt. Their data distributions are therefore coupled. As the forward policy becomes adventurous, it creates new recovery problems. As the reset policy improves, it permits more useful exploration.

The paper uses off-policy learning, which can reuse transitions for both objectives when the appropriate rewards are available. That is an efficiency opportunity, not a license to mix reward labels indiscriminately. The same action may be good for putting the puck in the goal and bad for returning it to the start. Each critic must retain the meaning of its own return.
''','Leave no Trace §4: forward/reset objectives and off-policy training.'),
C('Why the gate uses Q, not just V','actiongate',[
 ('A state can offer both good and bad actions',r'V_b(s)=\mathbb{E}_{a\sim\pi_b}[Q_b(s,a)]','This averages reset-policy actions.'),
 ('Evaluate the proposed forward action',r'Q_b(s,a_f)=\mathbb{E}[r_b+\gamma V_b(s^\prime)]','Take a_f once, then recover.'),
 ('Gate before the action happens',r'Q_b(s,a_f)<Q_{\min}\;\Rightarrow\;\text{abort}','Switch control without taking a_f.')],'''
Suppose the puck is one centimeter from the table edge. The reset policy can pull it inward, so the state value under that policy may be high. But the forward policy proposes a push outward. If we check only the state value, we approve an action using evidence about a different action. The danger occurs in the transition we failed to evaluate.

An action value solves this mismatch. The reset Q function asks: what reset return would I expect if I first took this particular proposed action, and then followed the reset policy? The initial action is supplied by the forward controller. The continuation is supplied by the backward controller. This mixed interpretation is exactly what makes the score relevant before execution.

The early-abort rule compares that score to a threshold. If the predicted reset return is too low, the proposed forward action is rejected and the reset controller takes over. The robot has not yet entered the successor state. This timing matters: deciding to recover after an irreversible transition is too late, even if the recovery detector is perfectly accurate afterward.
''','Leave no Trace §4.1 and Algorithm 1; original edge-of-table example.'),
C('What does a reset value measure?','discountreach',[
 ('Specify a one-time success reward',r'R_b=\mathbf{1}\{\tau_{\cal R}<\infty\}','End this illustrative return on success.'),
 ('Discounted success also prices delay',r'Q_b=\mathbb{E}[\gamma^{\tau-1}\mathbf{1}\{\tau<\infty\}]','Here success at the next transition has tau=1.'),
 ('Probability is a special case',r'\gamma=1\;\Rightarrow\;Q_b=\Pr(\tau<\infty)','Reward and boundary conventions matter.')],'''
A common shorthand calls the reset critic a probability of recovery. That can be a useful intuition, but we should derive the conditions under which it is literally true. In this teaching example, give a reward of one on the first successful reset transition, zero elsewhere, and stop the reset return at success. Let tau count transitions until that success.

The return is gamma raised to tau minus one if success occurs, and zero if it never occurs. Its expectation combines success probability with the time needed to succeed. When gamma is one, this becomes a recovery probability. When gamma is smaller, two policies with identical eventual success rates can have different values because one takes longer to return.

The paper also studies tasks with other reset rewards, so its numerical thresholds need not lie between zero and one. A threshold of point seven has no universal meaning independent of reward scale, discount, and termination convention. In our lab, we use an explicitly declared discounted first-success model. That makes the displayed scores interpretable without pretending they reproduce the paper's continuous-control critics.
''','Leave no Trace §4.1 probability intuition; original discounted first-hit derivation and convention.'),
C('A moving boundary of recoverability','recovermap',[
 ('Allowed state-action pairs',r'{\cal E}_{\rm allowed}=\{(s,a):Q_b(s,a)>q\}','The boundary lives in state-action space.'),
 ('A better reset skill can expand it',r'Q_b^{\rm new}(s,a)>Q_b^{\rm old}(s,a)','Learning changes the allowed set.'),
 ('Changing q also moves the boundary',r'q\uparrow\quad\Rightarrow\quad{\cal E}_{\rm allowed}\downarrow','For fixed scores, permission shrinks.')],'''
Visualize the reset value as a landscape over possible successor situations. Near the starting region, returning is easy and the landscape is high. Farther away, obstacles and uncertainty create valleys. A threshold draws a contour through that landscape. For a fixed critic, actions below the contour are rejected. More precisely, the contour belongs to state-action space, even when we draw a two-dimensional slice.

Now improve the reset policy. It learns to reach around an obstacle and recover from states that previously defeated it. Their reset values can rise, expanding the actions permitted to the forward learner. The constraint is learned and changes with competence. This is different from a fixed geometric wall specified by a designer before learning begins.

But increasing the threshold also shrinks exploration. If only already-mastered states are allowed, the system may never collect the data needed to improve recovery elsewhere. This creates a feedback problem: the critic controls what it gets to observe. Our visualization lets you move the threshold and the learned competence separately so you can see two distinct causes of an apparently cautious boundary.
''','Leave no Trace §4.1; original value-landscape visualization.'),
C('Estimate uncertainty with an ensemble','ensemble',[
 ('Several critics see the same query',r'\widehat Q_1,\ldots,\widehat Q_M','Different initializations give disagreement.'),
 ('Three summaries make different gates',r'\max_i\widehat Q_i,\quad\overline Q,\quad\min_i\widehat Q_i','Optimistic, mean, pessimistic.'),
 ('Compare each summary with the threshold',r'\widehat Q_{\rm summary}<q','A rejection rule, not a calibrated guarantee.')],'''
Consider an unfamiliar action for which three reset critics predict point two, point five, and point eight. Their disagreement is important. A single average hides the possibility that the action is much better or much worse than expected. Leave no Trace uses a bootstrap-style ensemble with differently initialized value functions to obtain a distribution of estimates for a query.

The paper considers three ways to turn those estimates into an abort. An optimistic gate aborts only when even the largest estimate is below the threshold. A mean gate compares the average. A pessimistic gate aborts when even one critic is below the threshold. With a threshold of point six, our example passes the optimistic gate but fails the other two.

These names describe a choice about exploration under disagreement. They do not establish calibrated confidence intervals or formal safety probabilities. Every critic could share the same modeling error, especially outside the training distribution. The interactive ensemble slider is therefore a sensitivity experiment: it shows how the decision rule reacts to scores, rather than claiming to measure a real robot's uncertainty reliably.
''','Leave no Trace §4.4; exact max/mean/min rules, original numerical example.'),
C('Optimism has a concrete price','ensemble',[
 ('Optimism can admit unfamiliar actions',r'\max_i\widehat Q_i\geq q','One hopeful critic can permit exploration.'),
 ('Pessimism demands broad agreement',r'\min_i\widehat Q_i\geq q','All critics must clear the threshold.'),
 ('Neither dominates every objective',r'\text{data gain}\quad\leftrightarrow\quad\text{reset cost}','The tradeoff is environment dependent.')],'''
Why would we ever choose the optimistic gate? Because unfamiliar does not mean impossible. If a reset policy has never tried a recoverable corner of the table, low initial estimates can lock that corner out forever. Allowing some uncertain actions can generate evidence, improve the reset controller, and eventually make the whole system less dependent on manual intervention.

The cost is that hopeful estimates can be wrong. An admitted action may enter a trap and require a hard reset. A pessimistic gate reduces exposure to such disagreement, but can also block the exploration needed to discover a viable route. In the paper's small gridworld study, excessive conservatism can prevent useful exploration. The continuous-control results do not imply one aggregation rule always wins.

When you inspect the lab, hold the true illustrative recovery score fixed and change only ensemble spread. Some rules change their decisions even though the toy environment has not changed. That isolates epistemic uncertainty from physical difficulty. It also reveals why a convenient slogan like higher uncertainty means stop is a design choice, not a theorem supplied by the reset critic.
''','Leave no Trace Appendix A; original epistemic-versus-dynamics experiment.'),
C('When do we request a hard reset?','attempts',[
 ('Run the learned recovery policy first',r'\pi_b:\;s\longrightarrow{\cal R}','A failed forward attempt may be recoverable.'),
 ('Observe repeated failed recovery attempts',r'{\cal S}_{\rm recent}\cap{\cal R}=\varnothing','The paper uses a finite attempt budget.'),
 ('Escalate when that budget is exhausted',r'N_{\rm attempts}\geq N','An operational decision under uncertainty.')],'''
Even a careful gate can make mistakes. Once the robot is in a difficult state, Leave no Trace first lets the reset policy attempt recovery. If it repeatedly fails to reach the designated reset region, the system requests a hard reset. The number of attempts is a parameter that trades continued autonomous effort against the cost of waiting in an unproductive state.

This is not a proof that the state is physically irreversible. A different policy might recover, or the current policy might succeed on its next stochastic attempt. Conversely, a truly absorbing trap can waste an arbitrarily long time if the attempt budget is too generous. The algorithm needs an operational stopping decision despite not knowing the full reachability structure.

In a toy model with independent attempts and fixed success probability, the chance of all N attempts failing is one minus that probability, raised to N. That equation helps interpret the budget, but real attempts are correlated and the state can change. We explicitly label the independence assumption in our illustration. Repeated failures provide evidence about a controller, not a complete characterization of the environment.
''','Leave no Trace §4.2; original independent-attempt toy model.'),
C('Read the full training loop','loop',[
 ('Propose, score, execute or hand off',r'a_f\sim\pi_f,\quad\widehat Q_b(s,a_f)\mathrel{?}q','The gate precedes execution.'),
 ('Improve both control problems',r'{\cal D}\longrightarrow(Q_f,\pi_f,Q_b,\pi_b)','Relabel rewards only when available.'),
 ('Count external intervention explicitly',r'N_{\rm hard}=\sum_t\mathbf{1}\{\text{external reset}_t\}','A learned reset still costs actions.')],'''
Read the algorithm as a cycle. During forward control, sample a proposed action and ask the reset critic to score it. If it passes, execute it, store the actual transition, and improve the relevant learners. If it fails, hand control to the backward policy without executing the rejected action. A forward time budget can also trigger the handoff.

During backward control, act toward the reset region and update from the collected experience. When the reset attempt ends, decide whether another task attempt is useful or whether repeated recovery failure warrants external intervention. Off-policy learning helps reuse the interaction stream, but its data handling still has to respect which reward and continuation each critic is estimating.

Three counters make the cycle easier to audit: forward interactions, recovery interactions, and hard resets. A method that reduces human intervention by spending many more robot actions may still be attractive, but that is a tradeoff to measure. The algorithm's central contribution is making recovery learnable and predictive, not making the cost of recovery disappear from the experiment.
''','Leave no Trace Algorithm 1; original accounting diagram.'),
C('Recoverability is narrower than safety','trap',[
 ('A return objective is specific',r'Q_b\;\text{predicts reset return}','It does not encode every hazard.'),
 ('A reversible action can still be harmful',r'\text{recoverable}\;\not\Rightarrow\;\text{harmless}','Reward design and constraints still matter.'),
 ('A learned score can be inaccurate',r'\widehat Q_b\ne Q_b','Estimate error matters at the gate.')],'''
The title connects resetting with safe exploration, and there is a clear reason: avoiding states from which recovery is impossible can prevent some important failures. But the mathematical object being estimated is reset return. It does not automatically represent every condition we care about. An action could be physically reversible while still damaging an object or violating another task constraint.

There is also a gap between the true reset value and a learned approximation. Even if high true value were the right criterion, approving actions using an inaccurate neural critic would not establish a formal guarantee. Ensemble disagreement can be informative, but agreement alone cannot rule out systematic error. Keep the estimated boundary distinct from an actually certified set of viable states.

This distinction helps you compare the next papers fairly. MEDAL focuses on useful starting distributions, RISC on efficient switching, and the no-regret paper on a precisely defined reset cost under explicit assumptions. None of those objectives should silently inherit a broader meaning. To evaluate a method, first state what its score predicts and what failure event its measurements count.
''','Interpretation and limits of Leave no Trace §§4–6; original comparison, not an additional theorem.'),
C('Try the gate yourself','actiongate',[
 ('Move the proposed action toward the edge',r'Q_{\rm toy}=p_{\rm recover}\gamma^{\tau-1}','Declared first-success toy score.'),
 ('Change threshold and aggregation',r'q,\;\min,\;\text{mean},\;\max','Watch which action is permitted.'),
 ('Separate the gate from ground truth',r'\widehat Q_{\rm gate}\quad\text{versus}\quad Q_{\rm toy}','The predictions can disagree with reality.')],'''
In the interactive recovery lab, the horizontal coordinate represents how far a proposed action pushes toward a difficult region. A declared analytic function assigns that action a toy probability of recovery and a recovery duration. Discounting combines those quantities into the displayed reference score. These functions make the exercise reproducible; they are not learned models from the paper.

Move the threshold upward and watch the permitted part of the action space shrink. Then introduce critic bias and spread. The reference curve stays in place, while three estimated critics move around it. Choose optimistic, mean, or pessimistic aggregation and inspect the gate's decision at the selected action. A visible gap between reference and estimate illustrates either false permission or unnecessary rejection.

Try to construct both mistakes deliberately. Make every critic overly optimistic near the edge, then make them overly pessimistic in an easy region. This experiment captures why the method is interesting: control, learning, and data coverage interact. It also prevents an attractive visual contour from being mistaken for an oracle. The contour is only as meaningful as its objective and its estimates.
''','Original laboratory model inspired by Leave no Trace; no benchmark or safety claim.'),
C('Recovery becomes part of exploration','roadmap',[
 ('Learn how to return',r'\pi_b','The backward policy creates future trials.'),
 ('Use that knowledge before acting',r'Q_b(s,a_f)','Action-conditioned evaluation is crucial.'),
 ('Next: choose the distribution to return to',r'\rho_b\approx\rho_{\rm demo}','MEDAL changes the reset target.')],'''
The key conceptual move is to train a skill for recovering and then use its value before the forward policy acts. That couples exploration to the ability to continue learning afterward. The action-conditioned query is essential: a state can be recoverable under one action and become a trap under another. Timing the check before execution makes the difference observable.

We also saw three limits. A discounted score need not be a literal probability. A learned ensemble does not certify correctness. A failed recovery budget does not prove physical irreversibility. These are not reasons to discard the method. They tell us how to interpret it, what to measure, and where a proposed extension would need additional evidence.

So far, the reset policy has tried to return toward the original starting region. But why should that be the best place to practice from throughout learning? In the next lesson, we will replace a single notion of going back with distribution matching. A classifier will become a reset reward, and useful demonstration states will become a curriculum for the forward learner.
''','Original synthesis; transition to MEDAL §4.')])
