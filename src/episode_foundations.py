from schema import chapter as C, episode
P='https://proceedings.mlr.press/v80/pardo18a.html'
E='https://arxiv.org/abs/2112.09605'
EPISODE=episode('foundations',1,'Foundations','What actually ends an episode?',
 'Time Limits in Reinforcement Learning + Autonomous Reinforcement Learning: Formalism and Benchmarking',
 'Fabio Pardo et al.; Archit Sharma et al.','2018 / 2022',P,'#67d9ef',
 'Separate the physical world, the return being learned, and the controller collecting data. Derive correct bootstrap targets before learning a reset policy.',
 [dict(title='Time Limits in Reinforcement Learning · ICML 2018',url=P),dict(title='EARL: Autonomous RL formalism · ICLR 2022',url=E)], [
C('The reset button is a hidden action','world',[
 ('A simulator gives you a fresh start',r's_0\sim\rho_0','A reset samples a start state.'),
 ('A robot inherits its last state',r's_{t+1}\sim P(\cdot\mid s_t,a_t)','Physical interaction continues.'),
 ('Account for the whole cycle',r'T=T_{\rm task}+T_{\rm recovery}+T_{\rm human}','All three costs matter.')],'''
Imagine teaching a robot to put a cup on a shelf. In a simulator, each attempt begins with the cup conveniently back on the table. That convenience is doing real work. Somebody, or some code with extraordinary powers, is reversing the previous attempt. Remove that reset button and the next attempt begins wherever the cup actually is. Learning must now create its own opportunities to practice.

Draw the physical state as a dot moving along a continuous curve. A training script may divide that curve into episodes, but drawing a vertical line does not move the dot. A controller switch also leaves the dot where it is. An external reset is different: it intervenes on the state, often using a person or a mechanism outside the learned action space.

Our central question is therefore larger than maximizing reward on one attempt. How does an agent make progress while preserving useful future attempts? We will track task time, recovery time, and human intervention. This series builds the necessary mathematics, then examines five approaches. Every numerical experiment in the companion is a transparent teaching example, rather than a reproduction of a paper's benchmark.
''','EARL formalism; original cup example and cost decomposition.'),
C('One trajectory, three kinds of boundary','boundaries',[
 ('Termination belongs to the task',r'd_{\rm term}\in\{0,1\}','The modeled return has ended.'),
 ('Truncation belongs to data collection',r'd_{\rm trunc}\in\{0,1\}','A batch or rollout has stopped.'),
 ('A handoff changes behavior',r'\pi_f\longrightarrow\pi_b','The physical state is continuous.')],'''
First distinguish three boundaries. Termination says the return we have defined has ended. If a task pays once when the cup reaches the shelf and then ends, that success can be terminal. A failure can also be terminal if the task specification says so. Terminal is a property of the modeled task, not a synonym for an inconvenient observation.

Truncation says we stopped collecting this segment. Perhaps a rollout buffer filled or a training timer expired. If the underlying task continues, the unobserved future still contributes value. A time limit can instead be part of the actual task, such as finishing within thirty seconds. We must decide which interpretation is intended before choosing a learning target.

A handoff is a third event. The forward controller yields to a recovery controller, but the world keeps evolving. That handoff need not terminate either controller's counterfactual goal-reaching value. In an off-policy learner, we can collect with one behavior and evaluate another policy. Keep these three labels separate in your replay data; a single undifferentiated done flag throws away meaning.
''','Pardo et al. §§2–3; RISC §4.1 supplies the controller-switch connection.'),
C('Derive the Bellman target','bellman',[
 ('Split off the first reward',r'G_t=r_t+\gamma G_{t+1}','This is an algebraic identity.'),
 ('Take a conditional expectation',r'V^\pi(s)=\mathbb{E}[r+\gamma V^\pi(s^\prime)]','Condition on state and policy.'),
 ('Mask only a true end',r'y=r+\gamma(1-d_{\rm term})V(s^\prime)','An artificial cutoff keeps the tail.')],'''
Let the discounted return be the reward now, plus gamma times the next reward, plus gamma squared times the following reward, and so on. Factor one gamma out of everything after the first reward. The entire future becomes gamma times the next return. This simple rearrangement is the source of the Bellman equation; it is not an arbitrary training convention.

Now condition on the current state and on following a policy. The conditional expectation of that future return is the value of the successor state. Because we rarely know the expectation exactly, a temporal difference update uses a sampled reward and an estimated successor value. The result is a bootstrap target: observed evidence now, plus an estimate of what remains.

If the modeled return truly ends, the remaining contribution is zero. Otherwise it remains present even when a data collector stops writing observations. This gives the termination mask on screen. Notice what is absent: neither a buffer boundary nor a controller switch automatically sets that mask. Their effects must follow from the return being evaluated, rather than from the shape of a software loop.
''','Pardo et al. §3; original step-by-step derivation.'),
C('A one-state counterexample','valuecurve',[
 ('A continuing reward stream',r'V=1+0.9V','One reward every transition.'),
 ('Solve its fixed point',r'V=\frac{1}{1-0.9}=10','The full tail is worth ten.'),
 ('A false end deletes value',r'y_{\rm correct}=10,\quad y_{\rm false}=1','Same transition, different target.')],'''
Consider the smallest possible continuing environment: one state, one action, and reward one on every transition. Let gamma be point nine. Because the state never changes, the Bellman equation says value equals one plus point nine times itself. Subtract point nine value from both sides and divide. The correct value is ten. Nothing about this calculation mentions episode length.

Suppose a collector cuts the trajectory after five steps. At that last recorded transition, a correct estimate produces target one plus point nine times ten, again ten. If we treat the cutoff as terminal, the target suddenly becomes one. The physical transition is identical to all the others, yet our labeling makes it look dramatically worse.

There is a useful quantitative extension. If a state-independent artificial cutoff occurs with probability p at each transition and we mistakenly mask it, the expected fixed point becomes one divided by one minus gamma times one minus p. With p equal to point two, that is about three point five seven. The interactive lab lets you move both parameters and see the bias grow.
''','Original analytic one-state example motivated by Pardo et al.; independent-cutoff assumption is explicit.'),
C('When a time limit really is the task','clockstate',[
 ('The same location can mean different things',r'V(s,h)\ne V(s,h-1)','Remaining time changes what is possible.'),
 ('Augment the state with time',r'\widetilde{s}=(s,h)','Restore the Markov description.'),
 ('Use the genuine boundary condition',r'V(s,0)=0','No task time remains.')],'''
Now change the task itself. The robot must deliver the cup before a deadline. A state two steps from success is promising when ten steps remain, and hopeless when only one step remains. If the observation includes only cup position, these two situations appear identical. A value network is being asked to assign two different answers to the same input.

The missing variable is remaining time. Augment the state with a clock, or otherwise make time inferable to the policy. The finite-horizon value is now a function of both state and steps remaining. Its recursion decrements the clock. At zero remaining steps, the task really has ended and the remaining value is zero, under this specified reward convention.

This is why always bootstrap and never bootstrap are both incomplete rules. Ask what process the critic is supposed to represent. A continuing task artificially sliced for training keeps its tail. A deadline-limited task includes time and has a genuine boundary. The paper's distinction is about mathematical consistency between the state, the objective, and the target, rather than a universal preference for longer episodes.
''','Pardo et al. §2: time limits intrinsic to the task versus partial episodes.'),
C('The final observation is part of the target','replay',[
 ('Store the actual transition',r'(s,a,r,s^\prime,d_{\rm term})','The successor precedes any reset.'),
 ('Do not substitute a fresh start',r's^\prime\ne s_{\rm reset}','Autoreset observations may be different.'),
 ('Keep the evaluated goal',r'y_g=r_g+\gamma(1-d_g)V(s^\prime,g)','A handoff does not silently relabel g.')],'''
Even with the correct mask, one implementation detail can quietly undo the reasoning. Some environment wrappers automatically reset after a boundary. The next observation they return may be a fresh start, while the final observation from the old trajectory is stored separately. Bootstrapping from that fresh start connects two states that were never connected by the recorded action.

Picture the replay tuple as a small causal diagram. The action leads from the current state to a particular successor, and the reward belongs to that transition. A separate reset arrow must not replace the successor arrow. Record the actual final observation before reset, and preserve separate termination and truncation information. The precise field names depend on the environment interface.

In goal-conditioned reset-free learning, preserve the goal associated with the value update too. If data collection changes from reaching the shelf to returning to the table, the old critic's target still concerns its old goal unless the algorithm explicitly relabels and recomputes rewards. A controller handoff changes future behavior; off-policy learning specifies how to estimate the desired continuation despite that change.
''','Pardo et al. partial-episode bootstrapping; original replay illustration; RISC §4.1.'),
C('Two objectives can disagree','objectives',[
 ('Deployment asks for a capable policy',r'J_{\rm deploy}=\mathbb{E}_{s_0\sim\rho_0}[V^\pi(s_0)]','Evaluate from the desired starts.'),
 ('Continuing evaluation scores the lifetime',r'J_{\rm life}=\liminf_{T\to\infty}\frac{1}{T}\mathbb{E}\!\left[\sum_{t<T}r_t\right]','Recovery consumes real interactions.'),
 ('Report the resources as well',r'(J_{\rm deploy},J_{\rm life},N_{\rm reset})','One scalar hides tradeoffs.')],'''
Suppose a robot reaches the shelf once and then keeps holding the cup there. If the reward is one whenever the cup is on the shelf, this behavior can score extremely well over its continuing lifetime. Yet it may have practiced moving the cup from the table only once. A second robot repeatedly takes the cup down and replaces it, sacrificing immediate reward to learn the full skill.

Which robot is better depends on the objective. Deployment evaluation asks how capable the learned policy is when started from the desired distribution. Continuing evaluation asks how much reward the learning system obtains over the interactions it actually experiences. EARL makes this distinction explicit. Recovery is useful for one objective even when it temporarily reduces the other.

For a clear experimental report, keep evaluation episodes separate from training interventions. A fresh start used to measure final competence does not automatically count as a training reset, but it should be disclosed. Also report environmental interactions, human resets, and elapsed recovery time. These quantities reveal whether an apparent gain came from better learning, easier evaluation starts, or an uncounted source of assistance.
''','EARL deployment and continuing evaluations; original shelf example and reporting guidance.'),
C('Resetting means controlling a distribution','occupancy',[
 ('The behavior induces visits',r'd^\pi(s)=(1-\gamma)\sum_{t\geq0}\gamma^t\Pr(s_t=s)','A normalized discounted occupancy.'),
 ('A backward policy changes future starts',r'\pi_b\longrightarrow\rho_{\rm next}','Recovery shapes the curriculum.'),
 ('Useful starts need not be identical',r'\rho_{\rm next}\approx\rho_{\rm useful}','The target depends on the objective.')],'''
The phrase reset suggests returning to one exact configuration. But learning often needs a distribution of useful starting situations. Represent the states visited by a policy as an occupancy distribution: add their visitation probabilities across time, discount them, and normalize. A controller changes not only the next action, but the distribution of future data seen by the learner.

When a backward policy runs between task attempts, its final states become the next forward starts. The reset policy is therefore also a curriculum generator. Sending the robot to the same distant starting configuration may be faithful to evaluation, yet difficult for discovering sparse rewards. Sending it to useful intermediate states may create practice opportunities that would otherwise be extremely rare.

There is an important distinction between a policy's occupancy and its final-state distribution. They are related by the dynamics and stopping rule, but they are not generally equal. Later, MEDAL will target demonstration-state occupancy as a practical way to create useful starts. We will keep that modeling step visible, rather than pretending that matching visits automatically proves every handoff distribution is optimal.
''','Original occupancy derivation; EARL objectives and MEDAL motivation.'),
C('Irreversibility is a property of the dynamics','trap',[
 ('A return path may exist',r'\Pr_\pi(\tau_{\cal R}<\infty)>0','Reach the reset region R.'),
 ('A trap may remove every return path',r'\sup_\pi\Pr_\pi(\tau_{\cal R}<\infty)=0','A better critic cannot create an action.'),
 ('Learned failure is different',r'\Pr_{\widehat\pi}(\tau_{\cal R}<\infty)\approx0','The current policy may simply be weak.')],'''
A cup can slide to the edge of a table and still be recoverable. Once it falls into a sealed bin outside the robot's reach, no available action may return it. On a state graph, the second situation is a region with incoming edges but no path back. No amount of additional value-function training can manufacture a missing physical action.

Now distinguish that structural impossibility from a weak reset policy. A robot may currently fail to pick up a cup that another policy could retrieve. Observed failure alone does not prove irreversibility. This distinction matters whenever an algorithm decides whether to keep trying, ask for assistance, or veto an action before it happens. Its judgment is based on limited evidence.

Reset-free methods consequently make different assumptions about recoverability, supervision, and permitted intervention. Some reduce manual resets empirically. Some learn indefinitely in reversible environments. A theoretical method may allow resets while bounding their growth. Read reset-free as a problem setting whose operational definition must be stated, rather than as an automatic promise of zero human assistance in every environment.
''','Leave no Trace §§4.1–4.2; original graph example; Nguyen & Cheng §3.'),
C('A hierarchy of questions','roadmap',[
 ('Can I get back?',r'Q_{\rm reset}(s,a)','Leave no Trace: recoverability.'),
 ('Where and when should I return?',r'\rho_{\rm target},\quad p_{\rm switch}','MEDAL and RISC: curricula.'),
 ('What can learning guarantee or imagine?',r'{\rm Regret}(K),\quad\widehat P','No-regret theory and MoReFree.')],'''
We can now organize the literature around questions rather than acronyms. Leave no Trace asks whether a proposed forward action leaves the reset controller enough ability to recover. Its critic becomes an action gate. MEDAL asks which states a backward controller should produce, using demonstrations to describe a useful distribution. These are related questions, but they change different parts of the system.

RISC asks when to switch between goals. Its surprising choice is to switch early when the current goal already looks easy, freeing interactions for less familiar regions. That is a different use of a value-like score from Leave no Trace, which aborts when recovery looks poor. Confusing those two decisions would invert the intended curriculum.

The no-regret paper asks what assumptions make performance and intervention guarantees possible. MoReFree asks how a learned world model can improve both exploration and practice while the physical environment continues. Throughout the series, use the same checklist: identify the objective, the state distribution, the return boundary, and the resource being counted. Those four choices explain much of the apparent disagreement between methods.
''','Original synthesis of the five primary papers linked in the series.'),
C('Work through the interactive laboratory','valuecurve',[
 ('Choose a discount and false-cutoff rate',r'\gamma\in[0,1),\quad p\in[0,1]','All values are computed analytically.'),
 ('Compare the fixed points',r'V_{\rm cut}=\frac{1}{1-\gamma(1-p)}','Only valid for this one-state toy.'),
 ('Inspect a single transition',r'y=r+\gamma(1-d)V_{\rm next}','Change termination independently.')],'''
Open the first laboratory and begin with gamma equal to point nine and an artificial cutoff probability of zero. Both value curves agree at ten. Increase the false-cutoff probability while keeping the continuing task unchanged. The incorrect value drops because each extra mask erases another expected piece of the future. The plot is calculated from the fixed-point equations, not from a hidden training run.

Next use the transition calculator. Enter reward one and successor value ten, then toggle true termination. With termination off, the target is ten; with termination on, it is one. Toggle only the collector cutoff and watch the correct target stay unchanged. This isolates semantics from estimation error: we have deliberately supplied the right successor value so that only the boundary decision varies.

Finally imagine replacing this one-state process with a deadline task. The calculator alone is now insufficient, because remaining time belongs in the state and the successor value depends on it. That limitation is the lesson. A formula can be correct for one modeled process and wrong for another. Before debugging an optimizer, make sure the quantities in its target describe the process you intended.
''','Original interactive exercise; analytic model, not an empirical learning result.'),
C('From a correct target to autonomous practice','roadmap',[
 ('Specify the return',r'G_t=\sum_{k\geq0}\gamma^k r_{t+k}','What future is the critic estimating?'),
 ('Specify the intervention',r'\pi_f\leftrightarrow\pi_b','What physically changes at a boundary?'),
 ('Specify the evaluation',r'\rho_0,\;T,\;N_{\rm reset}','What competence and costs are measured?')],'''
We started with an ordinary training convenience and uncovered three distinct mathematical objects. The return defines what the critic predicts. The physical transition process defines what the robot can actually do. The data-collection schedule defines what evidence it sees. Many reset-free learning bugs come from using one of those objects as a substitute for another.

A useful thought experiment is to pause a rollout just before a switch. Ask whether the old goal could still be pursued from that exact state. If so, its continuation value has not disappeared merely because another controller will collect the next action. Then ask whether the environment itself has been changed by an external intervention. That is a separate event to record and account for.

In the next lesson, we will make recovery an explicit learned skill. A forward action will have to pass a reset critic before being executed. We will derive what that critic means, examine why a high task reward can hide a bad future, and test how uncertainty changes the permitted region of exploration. The reset button becomes a control problem we can inspect.
''','Original synthesis and bridge to Leave no Trace.')])
