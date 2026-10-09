from schema import chapter as C, episode
P='https://arxiv.org/abs/2205.05212'
EPISODE=episode('medal',3,'MEDAL','Reset to a useful distribution',
 'A State-Distribution Matching Approach to Non-Episodic Reinforcement Learning',
 'Archit Sharma, Rehaan Ahmad, Chelsea Finn','2022',P,'#bea8ff',
 'Derive the optimal discriminator, the backward reward, and the Jensen–Shannon objective. See how demonstration states can shape a reset curriculum without copying expert actions.',
 [dict(title='MEDAL · primary paper',url=P)], [
C('Where should the next attempt begin?','curriculum',[
 ('Always returning to the start can be hard',r's_0\sim\rho_0','Sparse success may be far away.'),
 ('Demonstrations reveal useful states',r's\sim\rho_*','Include intermediate task states.'),
 ('Train the backward policy to visit them',r'\rho_b\approx\rho_*','The reset distribution becomes a curriculum.')],'''
Imagine a long corridor with a reward only at the far end. A beginner repeatedly starts at the entrance and wanders without ever seeing the reward. Now allow some attempts to begin at intermediate points visited by a successful demonstrator. The reward becomes discoverable, useful values can propagate backward, and the learner gets practice on meaningful parts of the task.

In a simulator, we might simply assign those initial states. A physical robot cannot teleport to them. MEDAL asks a backward policy to generate a useful state distribution through real actions. The important change is the target: instead of always matching the original starting region, the backward policy is encouraged to match states found in a small set of demonstrations.

We will derive the mechanism from a binary classification problem. A discriminator distinguishes demonstration states from backward-policy states. Its output becomes a reward for the backward controller. The resulting curriculum is learned through interaction. The companion laboratory uses small normalized histograms so that every probability, reward, and divergence can be inspected numerically rather than hidden inside a neural network.
''','MEDAL §§4.1–4.3; original corridor illustration.'),
C('States are the supervision, not expert actions','occupancy',[
 ('The target is a state marginal',r'\rho_*(s)','Sample states from demonstrations.'),
 ('The generator is a real controller',r'\rho_b=\rho^{\pi_b}','Dynamics constrain what can be visited.'),
 ('The forward policy still solves the task',r'\max_{\pi_f}\mathbb{E}\!\left[\sum_t\gamma^t r_f\right]','Distribution matching trains the backward side.')],'''
There are two distinct uses of demonstrations in robot learning. Behavioral cloning asks the policy to reproduce expert actions at expert states. State-distribution matching instead asks a process to visit a similar collection of states. Those goals need not produce the same behavior. Multiple action sequences can induce similar state marginals, especially when the environment has redundant control paths.

In MEDAL, the matching objective shapes the backward controller. The forward policy continues to optimize the task reward. Demonstration states describe promising places from which learning can proceed; they do not prescribe every recovery action. This is particularly helpful because a forward demonstration need not show how to reverse all the mistakes made during autonomous exploration.

The backward distribution is nevertheless constrained by the actual transition dynamics. If an expert state lies behind an unreachable barrier, a discriminator reward cannot make it reachable. Also distinguish the states visited throughout backward rollouts from the states at which control switches. MEDAL uses the former as a practical target that influences the latter, rather than assuming the two distributions are identical by definition.
''','MEDAL §4.2 and relationship to imitation learning; original marginal-versus-handoff clarification.'),
C('Turn distribution matching into classification','classifier',[
 ('Label demonstration states as one',r's\sim\rho_*:\;y=1','C(s) predicts demonstration membership.'),
 ('Label backward-policy states as zero',r's\sim\rho_b:\;y=0','Use the opposite class for generated states.'),
 ('Maximize binary log likelihood',r'\max_C\;\mathbb{E}_{\rho_*}\log C+\mathbb{E}_{\rho_b}\log(1-C)','This convention fixes the reward sign.')],'''
Suppose we can sample from two distributions but cannot evaluate their densities. We can still ask a classifier to distinguish them. Give demonstration states label one and backward-policy states label zero. Train the classifier with binary log likelihood: reward a large output on demonstrations and a small output on backward data. Equal class weighting is assumed in this derivation.

The labels are more than a cosmetic choice. If we reversed them, the algebraic form of the reward would have to reverse too. Many apparent disagreements between implementations come from different discriminator conventions. Here, a high classifier score always means this state looks more like the demonstration class relative to the current backward-policy class.

Now freeze the backward distribution and consider an ideal classifier with unlimited capacity. We can optimize its output separately at each state. That lets us solve the classification problem exactly, exposing the density ratio hidden inside it. The derivation is useful even though a finite neural classifier will only approximate the result and will be trained on a changing, imperfect sample of experience.
''','MEDAL Equation 3; original pointwise derivation setup.'),
C('Derive the optimal discriminator','densityratio',[
 ('At one state, write the objective',r'\ell(C)=a\log C+b\log(1-C)','a=rho_*(s), b=rho_b(s).'),
 ('Set its derivative to zero',r'\frac{a}{C}-\frac{b}{1-C}=0','Solve for the maximizing output.'),
 ('Recover a density ratio',r'C^*(s)=\frac{\rho_*(s)}{\rho_*(s)+\rho_b(s)}','Defined where the combined density is positive.')],'''
At a particular state, abbreviate the demonstration density by a and the backward density by b. The classifier's contribution is a times log C plus b times log one minus C. Differentiate with respect to C. The derivative is a divided by C minus b divided by one minus C. Setting it to zero gives a simple balance equation.

Multiply through by C times one minus C. We obtain a times one minus C equals b times C. Rearranging gives C equal to a divided by a plus b. The second derivative is negative wherever both densities are positive, so this stationary point is the maximum. States with zero combined density provide no classification information and need separate conventions.

Notice what the answer is not: it is not simply the demonstration density. A state receives a high score when demonstration mass is large relative to current backward mass. As the backward policy fills that region, the score decreases. The classifier therefore provides a moving signal about distribution mismatch, rather than a fixed map of which states are intrinsically good.
''','Original algebra for the optimal discriminator of MEDAL Equation 3.'),
C('The backward reward follows from the game','logreward',[
 ('The backward policy minimizes its term',r'\min_{\pi_b}\mathbb{E}_{\rho_b}\log(1-C(s))','Hold C fixed during this update.'),
 ('An RL agent maximizes reward',r'r_b(s)=-\log(1-C(s))','Negate the generator objective.'),
 ('At the ideal classifier',r'r_b(s)=\log\!\left(1+\frac{\rho_*(s)}{\rho_b(s)}\right)','Undersampled demonstration states are attractive.')],'''
The full objective is a minimax game. The classifier maximizes its ability to distinguish the two sources, while the backward policy minimizes that distinction. When the classifier is held fixed, the demonstration term is constant with respect to the backward policy. The policy only needs to minimize the expected log of one minus the classifier output on its own visited states.

Reinforcement learning conventionally maximizes rewards, so negate that quantity. The backward reward becomes minus log one minus C. Under our labeling convention, demonstration-like states produce larger rewards. Substitute the ideal classifier and simplify: the reward is log of one plus demonstration density divided by backward density. This reveals how the reward responds to missing coverage.

Consider a bin containing demonstration mass point three and backward mass point one. The ideal classifier outputs point seven five, producing a reward of about one point three nine. If both masses were point three, the classifier would output one half and the reward would be log two, about point six nine. The lab computes these values directly from the displayed histograms.
''','MEDAL §4.2 backward reward; original substitution and numerical example.'),
C('Why the equilibrium is distribution matching','jsdivergence',[
 ('Use the midpoint distribution',r'm=\tfrac12(\rho_*+\rho_b)','A shared reference for both densities.'),
 ('Substitute the optimal classifier',r'L(C^*,\rho_b)=-\log4+2\,\mathrm{JS}(\rho_*\Vert\rho_b)','The remaining discrepancy is a divergence.'),
 ('At equality, discrimination disappears',r'\rho_b=\rho_*\;\Rightarrow\;C^*=\tfrac12','Idealized expressive-function equilibrium.')],'''
We can also see the matching objective globally. Substitute the optimal discriminator into both terms of the minimax loss. Introduce the midpoint distribution, one half demonstration density plus one half backward density. Each denominator is twice this midpoint, so each logarithm splits into a density-ratio term and a minus log two constant.

The two density-ratio expectations are the two Kullback–Leibler divergences to the midpoint. Their average defines Jensen–Shannon divergence. Summing gives minus log four plus twice that divergence. Since the constant does not affect the minimizing distribution, the ideal backward generator minimizes the divergence between its state distribution and the demonstration distribution.

When the two distributions agree, the best classifier outputs one half wherever they have support. It cannot tell the sources apart. This is an idealized equilibrium under expressive function classes and successful optimization. In an actual robot, finite data, limited policies, unreachable states, and alternating updates can prevent exact matching. The equation explains the objective; it does not by itself prove convergence of a neural implementation.
''','MEDAL §4.2 idealized Jensen–Shannon interpretation; original derivation and limitations.'),
C('Matching visits creates learning opportunities','curriculum',[
 ('Sparse rewards need useful coverage',r'\Pr(\text{observe success})','Starting near useful states can help discovery.'),
 ('Forward values can propagate backward',r'V(s)\leftarrow r+\gamma V(s^\prime)','Intermediate successes teach earlier states.'),
 ('The final evaluation still has its own starts',r's_0^{\rm eval}\sim\rho_0','Training convenience does not redefine the task.')],'''
Return to the corridor. If the backward controller sometimes brings the learner near the goal, the forward policy can discover successful transitions. Those values can then support learning from earlier states, provided the data connects the regions. The demonstration distribution is a way to allocate practice along a successful route without requiring the reset policy to return all the way to the entrance every time.

This is a curriculum effect, not a change in the final task. A policy that succeeds only when started one step from the goal may still fail the deployment evaluation from the original start distribution. Training must eventually support competence over those desired starts. Useful intermediate practice is valuable because it can build that competence, not because it makes the evaluation easier by definition.

The paper motivates its choice using the importance of initial-state coverage for policy improvement and tests it on sparse-reward tasks. Our corridor illustration makes that motivation visible, but does not establish a universal sample-complexity improvement for arbitrary demonstrations. A demonstration can be narrow, unrepresentative, or physically irrelevant to states encountered during recovery. Distribution choice remains an assumption to examine.
''','MEDAL §4.1 motivation and §5 scope; original corridor curriculum interpretation.'),
C('Three coupled learners, one physical stream','loop',[
 ('Forward policy follows the task reward',r'\pi_f\longleftarrow r_f','Learn task completion.'),
 ('Backward policy follows classifier reward',r'\pi_b\longleftarrow-\log(1-C)','Learn useful state visitation.'),
 ('Classifier contrasts demonstrations and replay',r'C\longleftarrow(\rho_*,\rho_b)','The reward evolves as behavior changes.')],'''
The full system has three moving parts. The forward learner improves task performance. The backward learner improves the distribution of states encountered between attempts. The classifier updates its distinction between demonstration samples and backward-policy samples. These updates share one physical interaction stream, but they optimize different losses and can change on different time scales.

During a forward phase, execute task-directed actions and store transitions with task rewards. During a backward phase, execute reset-directed actions and compute classifier-based rewards on the resulting states. Update the discriminator from demonstration states and backward replay data. As the backward distribution changes, the classifier reward changes too. That nonstationarity is a real part of the method.

The original MEDAL setup assumes task rewards and demonstration data, with optional backward demonstrations described in the paper. Do not silently replace these with a completely unsupervised setting. Also distinguish this paper from later MEDAL-plus-plus work, which adds other components for autonomous visual robot learning. Here we are explaining the state-distribution matching mechanism itself and the resources it requires.
''','MEDAL Algorithm 1 and §4.3; distinction from later MEDAL++ work.'),
C('A discriminator is not a distance oracle','classifier',[
 ('Its output is relative to two data sources',r'C^*=\frac{\rho_*}{\rho_*+\rho_b}','Class priors and coverage affect interpretation.'),
 ('Zero support needs numerical care',r'\log(1-C)\quad\text{as}\quad C\to1','Clipping stabilizes a toy computation.'),
 ('State matching leaves behavior ambiguous',r'\rho^{\pi_1}\approx\rho^{\pi_2}\;\not\Rightarrow\;\pi_1=\pi_2','Marginals do not identify a policy.')],'''
A classifier score is tempting to interpret as geometric closeness to a demonstration. But the ideal formula depends on two densities, not Euclidean distance. A state can have a high score because backward data rarely visits it, even if it is not especially close to most demonstrations. Class weighting and replay sampling can further change the relationship between the score and the underlying distributions.

The logarithmic reward can also become numerically extreme when the classifier confidently separates the data. In the laboratory, we use a small positive floor before taking logarithms, and state that choice explicitly. It prevents undefined displays; it is not a theoretical solution to poor support overlap or unstable adversarial training. Those are learning problems requiring more than a plotting convention.

Finally, matching state marginals does not identify the expert policy or guarantee the same order of states. Two trajectories can visit the same bins in very different sequences. The environment and the task reward still determine whether those visits are useful. This is why our visual explanation keeps the trajectory view alongside the histogram instead of treating a matched histogram as the entire control problem.
''','Original limitations of the MEDAL discriminator objective; finite-bin illustration.'),
C('Compute a distribution-matching step','histogram',[
 ('Normalize both histograms',r'\sum_i p_i=\sum_i q_i=1','p is the demonstration target.'),
 ('Compute exact binwise scores',r'C_i=\frac{p_i}{p_i+q_i},\quad r_i=-\log(1-C_i)','No hidden fitted classifier in this lab.'),
 ('Take an illustrative reward-weighted step',r'q_i^+\propto q_i\exp(\eta r_i)','A distribution update, not a robot policy optimizer.')],'''
The MEDAL lab has eight state bins. One histogram represents demonstration states; the other represents backward visits. Change the concentration and location of the backward histogram and inspect each bin's optimal classifier score and reset reward. The interface also computes Jensen–Shannon divergence from the normalized distributions, using the midpoint formula we derived.

Press the distribution-step button to apply a simple exponentiated reward update. Each current bin mass is multiplied by the exponential of its reward times a learning rate, and then the masses are normalized. This is a deliberately simplified distribution-space experiment. It illustrates the direction of the incentive while avoiding the claim that a real policy can independently assign arbitrary probability to every state.

After each step, recompute the optimal discriminator for the new histogram. Regions that were undersampled become less distinguishable as mass arrives. Try a large step size and observe that aggressive updates need not make a smooth monotonic path in this toy alternating procedure. Then reset the experiment. The mathematical equilibrium and the behavior of a finite update rule are related, but they are different claims.
''','Original finite-bin lab and exponentiated update; MEDAL objective supplies the reward, not this optimizer.'),
C('What evidence would validate the curriculum?','comparison',[
 ('Measure deployment competence',r'J(\pi_f;\rho_0)','Use the intended evaluation starts.'),
 ('Count training resources',r'(T_f,T_b,N_{\rm human})','Include backward actions and demonstrations.'),
 ('Ablate the target distribution',r'\rho_0\quad\text{versus}\quad\rho_*','Isolate what distribution matching changes.')],'''
To test the central idea, compare backward policies trained toward different target distributions while holding the rest of the learning system as consistent as possible. Returning to the original start region tests one hypothesis. Matching demonstration states tests another. Measure task competence from the same evaluation distribution so that an easier testing setup cannot masquerade as a better curriculum.

Count backward interactions as well as forward interactions. Record the number and kind of demonstrations, the task reward information provided, and any manual resets during training. If the classifier uses privileged state information, that matters too. An algorithm can be very useful with those resources, but the resource description is part of what another researcher needs to reproduce the comparison.

The paper reports benefits on its tested sparse-reward settings. Our explanatory plots do not copy those empirical curves or invent performance numbers. They isolate the classifier objective and show why it can encourage useful coverage. The gap between that mechanism and a successful end-to-end robot is precisely where dynamics, representation, optimization, and evaluation design enter the research question.
''','MEDAL §5 evaluation scope; original experimental reasoning, no synthetic benchmark results.'),
C('From where to reset, to when to switch','roadmap',[
 ('Demonstrations define a target distribution',r'\rho_*','Useful states guide practice.'),
 ('Classification defines a reset reward',r'r_b=-\log(1-C)','The sign follows from the label convention.'),
 ('The next question is timing',r'p(\text{switch}\mid s,g,t)','RISC changes how long each phase runs.')],'''
MEDAL turns a practical question, where should the robot practice next, into a distribution-matching game. The derivation starts from labeled samples, gives an optimal density-ratio classifier, and converts the generator's objective into a reset reward. At ideal equilibrium, the backward occupancy matches the demonstration-state distribution and the classifier can no longer distinguish the sources.

The mechanism comes with a clear set of qualifications. The policy cannot ignore dynamics. Occupancy and handoff distributions are related but distinct. A finite classifier can be wrong. A state marginal does not specify action sequences. Most of our useful understanding comes from keeping those qualifications attached to the equations, rather than dropping them after drawing a neat adversarial-learning diagram.

We have now changed the destination of recovery. The next paper changes its timing. Even if the current goal is appropriate, continuing all the way to it may spend most of the interaction budget on a region the agent already knows. RISC uses a success critic to decide when to hand off early, while preserving the value targets of the underlying goal-conditioned control problem.
''','Original synthesis; transition to RISC.')])
