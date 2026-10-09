from schema import chapter as C, episode
P='https://arxiv.org/abs/2408.09807'
EPISODE=episode('morefree',6,'MoReFree','Practice in a model, return in the world',
 'Reset-free Reinforcement Learning with World Models',
 'Zhao Yang, Thomas M. Moerland, Mike Preuss, Aske Plaat, Edward S. Hu','TMLR 2025',P,'#86c5ff',
 'Follow the world-model learning loop, derive the goal mixture, and distinguish imagination goals from real back-and-forth exploration. Examine model error without inventing benchmark results.',
 [dict(title='MoReFree · published-version paper',url='https://arxiv.org/html/2408.09807v3'),dict(title='Authors’ project and videos',url='https://yangzhao-666.github.io/morefree/')], [
C('An explorer can forget why it is exploring','world',[
 ('Novelty can pull data away from the task',r'\pi_E\longrightarrow\rho_{\rm unfamiliar}','Interesting does not always mean relevant.'),
 ('A reset no longer restores the useful region',r's_{t+1}\sim P(\cdot\mid s_t,a_t)','The next data point depends on the current state.'),
 ('Bias both exploration and practice toward relevance',r'\rho_0,\quad\rho_{g^*}','Initial states and evaluation goals matter.')],'''
Imagine a mobile robot rewarded for discovering unfamiliar parts of a warehouse. It finds a complicated corner with endless novelty and stays there. Meanwhile, the actual deployment task is moving between a loading station and a shelf. In an episodic benchmark, automatic resets repeatedly bring the robot back to relevant areas. Without them, the learning system must create that return behavior itself.

A world model can help the robot learn from fewer physical interactions by simulating possible futures. But a model trained mostly on irrelevant corners can still allocate practice poorly. Strong exploration alone does not ensure that the collected data supports the task. The question becomes both where to act in the real world and which goals to train toward inside the learned model.

MoReFree modifies both choices. It periodically directs real behavior between initial states and evaluation goals, and it biases imagined goal practice toward those same task-relevant distributions. The published paper is titled Reset-free Reinforcement Learning with World Models. We will distinguish the two sampling mechanisms, derive their consequences, and keep model-based efficiency separate from the physical work of recovery.
''','MoReFree §§1,4; original warehouse illustration. Uses the TMLR 2025 / arXiv v3 title.'),
C('A learned simulator inside the learner','worldmodel',[
 ('Fit a predictive model from real transitions',r'\widehat P_\theta(z_{t+1}\mid z_t,a_t)','A latent dynamics model.'),
 ('Roll out candidate behavior in the model',r'\widehat z_{t+1}\sim\widehat P_\theta(\cdot\mid\widehat z_t,a_t)','Imagination produces training trajectories.'),
 ('Return to reality for new evidence',r'{\cal D}_{\rm real}\longrightarrow\widehat P_\theta\longrightarrow\pi','Predictions are grounded by collected experience.')],'''
The model-based backbone learns a recurrent state-space model from interaction data. A latent state summarizes the information used to predict what happens after an action. The model then acts as a learned simulator: policies can generate synthetic trajectories inside it, and value functions can learn from the predicted consequences. These computations do not require physically executing every imagined action.

There are two important policies in this backbone. A goal-conditioned policy tries to reach a commanded state, while an exploration policy seeks informative experience. Both are trained using imagined rollouts. Real data still updates the model and constrains what it knows. The cycle is collect, model, imagine, improve, then collect again with the improved behavior.

The equations on screen deliberately describe the concept rather than pretending to reproduce every recurrent-network training term. MoReFree builds on PEG and its Dreamer-derived model-based machinery. Its central changes concern how exploration is organized and which goals are used in policy learning. Keeping the inherited backbone separate from the new choices helps identify what the paper actually contributes.
''','MoReFree §3.2; conceptual latent-model notation, not the complete RSSM loss.'),
C('Learn a goal-reaching reward from temporal distance','distance',[
 ('Sample state pairs from imagined trajectories',r'(z_t,z_{t+k},k)','The separation provides supervision.'),
 ('Predict normalized dynamical distance',r'd_\omega(z_t,z_{t+k})\approx\frac{k}{H_{\rm imag}}','A learned action-distance signal.'),
 ('Train goal reaching with negative distance',r'r_G(z,g)=-d_\omega(z,g)','Environmental task rewards are not required for this training signal.')],'''
How can the goal-conditioned policy train without the environment's task reward? The backbone learns a dynamical distance function. Sample two states from an imagined trajectory and use their temporal separation as supervision. The function predicts how many actions separate a state from a goal, with the normalization described in the paper's appendix. This is a learned control-related distance, not ordinary geometric distance.

Negate that predicted distance to obtain a goal-reaching reward. States estimated to be closer to the commanded goal receive a better score. The policy learns to reduce this distance in imagination. Because the distance is learned from trajectories, its usefulness depends on the quality of the model, the policy generating those trajectories, and the coverage of the sampled state pairs.

There is no claim that all task specification has disappeared. The method still assumes relevant initial-state and evaluation-goal distributions. Those tell the system what starts and destinations matter. Removing environmental reward supervision differs from removing goals, representations, and reset assumptions. The learned distance provides a training signal within that specified goal-conditioned problem, rather than discovering an arbitrary user's intent from no information.
''','MoReFree §3.2 and Appendix C.1; normalized distance target k/H and reward -d.'),
C('The Go-Explore building block','goexplore',[
 ('Go toward a selected goal',r'g\sim\rho,\quad a_t\sim\pi_G(\cdot\mid s_t,g)','Run for H_G real steps.'),
 ('Explore from the state actually reached',r'a_t\sim\pi_E(\cdot\mid s_t)','Run for H_E additional real steps.'),
 ('Store the continuous trajectory',r'\tau_{\rm Go}\mathbin{\|}\tau_{\rm Explore}','No teleport between the phases.')],'''
The physical data-collection primitive has two phases. First choose a goal and run the goal-conditioned policy for a specified horizon. Then, from whatever state was actually reached, run the exploration policy for another horizon. Store both segments. The phrase Go-Explore names this alternation between directed movement and exploration from the resulting location.

In the PEG backbone, exploratory goals are selected using the learned model to seek useful exploration opportunities. The exploration policy is trained with an intrinsic signal based on disagreement among prediction models. Disagreement can encourage visiting areas where the model may improve. But the connection between uncertainty, learning progress, and task relevance is imperfect, especially when the physical process is never routinely reset.

If every chosen goal pulls farther into unfamiliar but irrelevant regions, the system can neglect the starts and goals used at evaluation. A model may become very knowledgeable about the wrong places. MoReFree keeps the Go-Explore primitive but changes how it is scheduled around task-relevant goal pairs. The next animation makes those physical phases explicit so that learned resets cannot be confused with simulator resets.
''','MoReFree Algorithms 1–2, §3.2 and Appendix C.3; original relevance interpretation.'),
C('Back-and-forth exploration in the real world','backforth',[
 ('Choose the task-directed branch with probability alpha',r'b\sim\mathrm{Bernoulli}(\alpha)','One decision selects a routine.'),
 ('On that branch, execute two Go-Explore calls',r'g^*\sim\rho_{g^*}\quad\text{then}\quad g_0\sim\rho_0','Forward and back, from actual successive states.'),
 ('Otherwise use an exploratory goal',r'g_E\sim\rho_E\quad\text{with probability}\;1-\alpha','Preserve broad exploration.')],'''
At each outer data-collection decision, draw a coin with probability alpha. If it selects the task-directed branch, sample an evaluation goal and an initial-state goal. Execute Go-Explore toward the evaluation goal, then execute Go-Explore toward the initial-state goal. The second call begins from the actual final state of the first call, including its exploration phase.

This order creates forward and back behavior through ordinary actions. The policy may fail to reach a sampled goal within its allotted horizon, so the procedure does not assume successful teleportation. It keeps operating from the state it has. On the other branch, with probability one minus alpha, execute one Go-Explore call for an exploratory goal supplied by the backbone.

The mixture balances task relevance with wider exploration. A small amount of directed return can bring data collection back to states that matter for evaluation and future practice. But if the policy cannot yet reach them, merely sampling those goals is not enough. That motivates the second change: explicitly training the goal-conditioned policy on relevant goals inside the learned model.
''','MoReFree §4.1 and Algorithm 3; physical continuity and possible goal failure made explicit.'),
C('A different mixture governs imagined practice','mixture',[
 ('Sample evaluation goals in imagination',r'\Pr(g\sim\rho_{g^*})=\frac{\alpha}{2}','Practice the task destination.'),
 ('Sample initial-state goals too',r'\Pr(g\sim\rho_0)=\frac{\alpha}{2}','Practice the return destination.'),
 ('Keep replay goals for general competence',r'\rho_{\rm imag}=(1-\alpha)\rho_{\cal D}+\frac{\alpha}{2}\rho_{g^*}+\frac{\alpha}{2}\rho_0','These weights sum to one.')],'''
The goal-conditioned policy also needs practice reaching the destinations that real behavior will request. During imagined policy training, MoReFree samples evaluation goals with probability alpha over two, initial-state goals with the same probability, and random replay states with the remaining probability one minus alpha. The three mixture weights add to one.

The replay component maintains broader goal-reaching ability. The two task-relevant components emphasize what evaluation and back-and-forth exploration will demand. If the model can support those imagined trajectories, the policy can improve its ability to return without physically repeating every training rollout. This is how sample efficiency in imagination can support autonomy in the real environment.

Keep this mixture separate from the real-world branch coin. The same alpha parameter appears in both, but the procedures are different. One chooses among individual goals for imagined learning. The other chooses between a two-call task-directed routine and a one-call exploratory routine. Equating their raw percentages would miss a subtle but important difference in how interaction time is allocated.
''','MoReFree §4.2 and Algorithm 2; exact alpha/2, alpha/2, 1-alpha goal weights.'),
C('A branch probability is not a time fraction','callfraction',[
 ('A relevant branch contains two calls',r'\mathbb{E}[N_{\rm relevant}]=2\alpha','One forward and one back Go-Explore call.'),
 ('An outer decision contains one or two calls',r'\mathbb{E}[N_{\rm all}]=2\alpha+(1-\alpha)=1+\alpha','Assume equal call lengths.'),
 ('The long-run relevant-call fraction is different',r'f_{\rm relevant}=\frac{2\alpha}{1+\alpha}','An analytic consequence of the schedule.')],'''
Here is a small calculation that makes the distinction concrete. Every task-directed outer decision generates two Go-Explore calls. Every exploratory outer decision generates one. Over many independent decisions, the expected number of task-directed calls per decision is two alpha, while the expected total is one plus alpha. With equal call lengths, their long-run ratio is two alpha divided by one plus alpha.

At alpha equal to point two, the imagined goal distribution assigns ten percent to evaluation goals, ten percent to initial-state goals, and eighty percent to replay goals. But the real schedule assigns about one third of its Go-Explore calls to the paired task-directed branch. Those calls still contain their own exploration phases, so this is not a claim that one third of all actions are direct goal pursuit.

This ratio is our accounting derivation from the pseudocode, not a performance statistic reported by the paper. It assumes the specified fixed phase lengths and enough calls for the long-run average to be meaningful. The laboratory shows both the imagined-goal mixture and this derived call fraction, preventing two uses of alpha from being collapsed into a misleading single pie chart.
''','Original renewal/accounting calculation from MoReFree Algorithm 3; equal call lengths assumed.'),
C('Imagination does not reset the physical robot','worldmodel',[
 ('An imagined state can be chosen computationally',r'\widehat z_0\sim{\cal D}','A model rollout can branch from stored experience.'),
 ('The physical state follows real actions',r's_{t+1}\sim P(\cdot\mid s_t,a_t)','Recovery still requires actual control.'),
 ('Model learning and recovery form a loop',r'\text{coverage}\to\widehat P\to\pi_G\to\text{coverage}','Better practice needs better evidence.')],'''
A learned simulator gives the optimizer a convenient capability: it can begin synthetic trajectories from stored latent states and explore hypothetical futures. That computational freedom can resemble a reset button. But it belongs to the model, not to the robot. The real system remains in its actual state until real actions move it somewhere else.

This creates a feedback loop. Real coverage trains the model. The model supplies imagined practice. Practice improves the goal-conditioned policy. That policy then changes which real states can be reached and recovered from. If one link fails, the others can suffer. A model with poor recovery data may imagine easy returns that the physical policy cannot reproduce.

The two MoReFree changes aim to strengthen the loop together. Task-directed real exploration supplies relevant evidence, and task-directed imagined goals train the skills that exploration requests. The paper's ablations examine those components. Our diagram shows their causal roles without treating imagination as a source of guaranteed correct transitions or a replacement for measuring actual intervention during data collection.
''','MoReFree §§4–5 ablation motivation; original model-versus-physical-reset distinction.'),
C('Long imagined rollouts can compound error','modelerror',[
 ('A transparent one-dimensional toy',r's_{t+1}=s_t+a','The true dynamics use unit gain.'),
 ('Let the model have a fixed gain bias',r'\widehat s_{t+1}=\widehat s_t+(1+\epsilon)a','Same constant action in both systems.'),
 ('After H steps, the discrepancy is explicit',r'|\widehat s_H-s_H|=H|\epsilon a|','This linear accumulation is specific to the toy.')],'''
To see why imagination requires care, use a one-dimensional system whose true next state is current state plus action. Give the learned model a small multiplicative bias on that action. If both systems begin at the same state and repeat the same constant action, each model step adds an extra epsilon times action. After H steps, the discrepancy is H times that error.

This is a deliberately simple example. Real closed-loop nonlinear dynamics can amplify, damp, or redirect errors, so there is no universal claim that all world-model error grows linearly. The toy lets us isolate the relation between rollout length and a persistent prediction bias. A tiny one-step error can become a meaningful difference over a long imagined control sequence.

A policy optimizer may also prefer trajectories where the model is unrealistically optimistic. Increasing the number of imagined samples does not remove that bias; it can reinforce it. The paper discusses limitations of model-based learning and cases where learning dynamics can be difficult. Strong empirical performance on its tasks should be interpreted alongside those limits, not as proof that a world model solves every reset-free environment.
''','Original constant-gain-error example; MoReFree discussion and Appendix F for model limitations.'),
C('Interpret the evidence and supervision carefully','comparison',[
 ('The training signal is self-supervised',r'r_G=-d_\omega','No environmental reward or demonstrations for MoReFree’s training signal.'),
 ('The task still supplies relevant distributions',r'\rho_0,\;\rho_{g^*}','Goals and starts remain specified.'),
 ('Evaluation measures episodic goal-reaching competence',r'J(\pi;\rho_0,\rho_{g^*})','Distinguish evaluation starts from training resets.')],'''
MoReFree is evaluated in a goal-conditioned reset-free setting with episodic evaluation. Policies are tested from the initial-state distribution toward evaluation goals. During training, the system uses a learned distance reward and model-based exploration rather than environmental task reward or demonstrations. Those are meaningful reductions in supervision, but the initial and evaluation-goal distributions are still supplied.

The published study compares methods on eight tasks and includes ablations of real exploration and imagined goal sampling. Its conclusions are empirical within those environments and implementations. The explanation here does not introduce new benchmark scores, real-robot deployments, or a formal reset-rate guarantee. Our charts are analytic teaching models whose parameters are visible and whose limitations are stated next to the controls.

When reading a model-based result, ask separately whether it improves final goal-reaching performance, physical sample efficiency, recovery behavior, and dependence on external intervention. Also inspect the observation representation and supervision available to each baseline. These questions make it possible to appreciate the method's contribution without treating a favorable learning curve as evidence for every possible meaning of autonomy.
''','MoReFree §§3.1,5 and Table 1; original evaluation checklist grounded in the paper’s scope.'),
C('Use the world-model laboratory','mixture',[
 ('Change alpha and compare two allocations',r'\rho_{\rm imag}\quad\text{and}\quad\frac{2\alpha}{1+\alpha}','Goal weights versus real routine call share.'),
 ('Change horizon and model bias',r'H,\;\epsilon','Trace true and predicted toy trajectories.'),
 ('Interpret each number under its own assumptions',r'\text{allocation}\ne\text{performance}','More relevant practice is a mechanism to evaluate.')],'''
The final laboratory has two linked views. The first computes the three imagined goal probabilities exactly from alpha, alongside the derived task-directed call fraction in the real schedule. Start at the paper's default alpha of point two, then move toward zero and one. At zero, no task-directed bias remains. At one, replay-goal training and exploratory-only routines are removed in this simplified accounting.

The second view compares true and predicted one-dimensional rollouts. Adjust the gain bias and the imagination horizon. The displayed final discrepancy is computed from the trajectories and agrees with the analytic formula. Set bias to zero to make the paths coincide; increase horizon to expose accumulated error. There is no trained world model hidden behind these lines.

Read the views together. Goal allocation can focus learning on relevant behavior, while model error can make that practice misleading. Neither slider directly predicts the paper's benchmark performance. The purpose is to make two causal ingredients inspectable: which tasks receive training effort, and how trustworthy imagined consequences are. A successful system needs both useful allocation and adequate predictive accuracy in the regions it relies on.
''','Original interactive allocation and dynamics labs; alpha=0.2 is MoReFree §4.3 default.'),
C('One continuous world, several learning decisions','roadmap',[
 ('Preserve the meaning of value',r'y=r+\gamma(1-d_{\rm term})V(s^\prime)','Termination is a property of the modeled return.'),
 ('Choose recovery, destinations, and timing',r'Q_b,\quad\rho_b,\quad p_{\rm switch}','Leave no Trace, MEDAL, and RISC.'),
 ('Separate mechanisms from guarantees',r'\widehat P\quad\text{versus}\quad\mathrm{Resets}(K)=o(K)','MoReFree and no-regret theory answer different questions.')],'''
Across the series, we have treated the world as one continuing process and identified the decisions a reset button used to hide. The foundations lesson separated task termination from collection boundaries. Leave no Trace learned recovery and used it to screen actions. MEDAL selected useful return distributions. RISC chose when to switch based on competence while preserving the critic's meaning.

The theory paper supplied a different kind of understanding: an assumption-to-guarantee chain linking no-regret learning to performance and expected reset cost. MoReFree supplied a model-based mechanism for improving relevant practice through both real exploration and imagination. These ideas can inform one another, but their assumptions and conclusions should remain visible when proposing combinations.

The common design question is how today's experience affects tomorrow's ability to keep learning. Answer it by specifying the return, the reachable states, the data distribution, the behavior schedule, and the intervention budget. Then use the experiments to challenge your intuition. A reset-free learner is not merely an episodic learner with one function call removed; it is a system responsible for creating its own future practice.
''','Original synthesis of all six lessons; no claim of a combined algorithm or new guarantee.')])
