Title: [转] Stacked Diffs Versus Pull Requests
Date: 2022-03-25 11:16:16
Category: 工具
Tags: 转载, git
CommentId: X

原文作者: [Jackson Gabbard](https://twitter.com/jgbbrd)

原文链接: [https://jg.gg/2018/09/29/stacked-diffs-versus-pull-requests/](https://jg.gg/2018/09/29/stacked-diffs-versus-pull-requests/)

为防遗失，转载一份


<!-- PELICAN_END_SUMMARY -->


Update: This post received quite a lot of healthy discussion on Hacker News. You can follow that conversation here: [https://news.ycombinator.com/item?id=18119570](https://news.ycombinator.com/item?id=18119570)

Update: And… again? [https://news.ycombinator.com/item?id=26922633](https://news.ycombinator.com/item?id=26922633)

Update: Btw, if you want to work this way, [we're hiring at Cord](https://cord.com/jobs) !

People who have worked with [Phabricator](https://www.phacility.com/phabricator/) using a 'stacked diff' workflow generally love it and seek it wherever they next go. People who have never used it and only use Pull Requests with GitHub/GitLabs generally don't understand what the fuss is all about. How can code review be \*sooo\* much better using some obscure tool with hilarious documentation? Well, hold on to your butts, because I'm about to break it down. This post is going to focus solely on the engineering workflow for committing code and getting reviews. I'll probably do a second post about the details of code review between the two tools.

<div class="mynotation">
<p>Phabricator 已经不再维护了。而 Gerrit 又太丑。<a href="https://www.reviewboard.org/">Review Board</a>值得一试。</p>
<p>命令行工具可以试试 <a href="https://github.com/gitext-rs/git-stack">git-stack</a> 。</p>
</div>

Before I dig deeply, let me just say I've created and merged hundreds of Pull Requests and landed thousands of Diffs. I know both of these workflows in and out. I'm not just some ex-Facebook, Phabricator fan boy pining for the 'good old days.' I've worked on engineering teams using CVS (oh yes), SVN, Git, and Mercurial. GitLabs, GitHub, Gerrit, and Phabricator. I'll happily acknowledge that you can get a lot of good work done using any of these. Now, if you want to talk about how to get the most work done — the most productivity per engineer — that's where I have a strong opinion informed by lots of experience.

## What are stacked diffs?

Many folks reading this post won't actually have a clue what "stacked diffs" are all about anyway. This is understandable. Feature branches and Pull Requests (PRs) are fairly ubiquitous and (sort of) well-understood. For the uninitiated, I'll outline how it works.

### First, Pull Requests

In PR-based development, you start by branching master then add one or more commits which you submit as a 'Pull Request' in the Github UI. A Pull Request is (or at least should be) an atomic unit of code for review. When someone requests changes, you do this by adding additional commits to the pull request until the sum of these changes satisfies the reviewers demands.

The really important thing about this is that the state of your local repository is dictated by the review process. If you want to have your code reviewed, you first have to branch master, then commit to that branch, then push it remotely, then create a PR. If you get review feedback, you have to commit more code onto the same branch and a) push it to create a longer, less coherent commit history or b) merge your local commits and force push to the branch. This also means that you can't have a local checkout of the repository that looks different from the remote. This is a really, really important point that I'll come back to again and again.

### So, Stacked Diffs

The basic idea of stacked diffs is that you have a local checkout of the repository which you can mangle to your heart's content. The only thing that the world needs to care about is what you want to push out for review. This means you decide what view of your local checkout the reviewers see. You present something that can be 'landed' on top of master. It may be helpful to skip down to the Case Studies section below to get a more intuitive feel about how this works.

The typical workflow is to work right on top of master, committing to master as you go. For each of the commits, you then use the Phabricator command line tool to create a 'Diff' which is the Phabricator equivalent of a Pull Request. Unlike Pull Requests, Diffs are usually based on exactly one commit and instead of pushing updates as additional commits, you update the single commit in place and then tell Phabricator to update the remote view. When a Diff gets reviewed and approved, you can "land" it onto remote master. Your local copy and master don't have to be in perfect sync in order to do this. You can think of this as the remote master cherry-picking the specific commit from your git history.

That's right, I said it. You can probably commit everything to master. Sound terrifying? It's mostly… well… just, not a problem at all. It's fine like 93% of the time. In fact, this approach gives you the ability to do things that branches alone just can't (more on that below). The anxiety many engineers feel about committing ahead of master is a lot like the fear that if you fly at lightspeed, you'll crash into a star. Popularly held, theoretically true, and practically completely wrong.

In practice, engineers tend to work on problems whose chunks don't easily divide into units of code review that make sense as a branch-per-unit-of-review. In fact, most engineers don't know exactly how their work decomposes when they start working on a problem. Maybe they could commit everything to master. Maybe they need a branch per commit. Maybe it's somewhere in between. If the rules for how to get code reviewed and how to commit code are defined for you ahead of time, you don't get to choose, which in many cases means a net loss in productivity.

The big "aha!" idea here is that units of code review are individual commits and that those commits can stack arbitrarily, because they're all on one branch. You can have 17 local commits all stacked ahead of master and life is peachy. Each one of them can have a proper, unique commit message (i.e. title, description, test plan, etc.). Each of them can be a unit out for code review. Most importantly, each one of them can have a single thesis. This matters *so* much more than most engineering teams realize.

### Yes, basically every commit can be on top of master

"But that's marmot floofing crazy!" I hear you say at your computer, reading this months after the blog post was written. Is it? Is it, really?! You may be surprised to learn that many engineers, who make a fantastic amount of money from some of the best companies in the world, commit directly to master all of the time, unless they have a reason not to.

To enable this, the mental model is different. A unit of code review is a single commit, not a branch. The heuristic for whether or not to branch is this: 'Am I going to generate many units of code review for this overall change?' If the answer is yes, you might create a branch to house the many units of code review the overall change will require. In this model, a branch is just a utility for organising many units of code review, not something forced on you \*as\* the mechanism of code review.

If you adopt this approach, you can use master as much as you want. You can branch when/if you want. You, the engineer, decide when/if to branch and how much to branch.

In this model, every commit must pass lint. It must pass unit tests. It must build. Every commit should have a test plan. A description. A meaningful title. Every. Single. Commit. This level of discipline means the code quality bar is fundamentally higher than the Pull Request world (especially if you rely on Squash Merge to save you). Because every commit builds, you can bisect. You can expect that reading pure `git log` is actually meaningful. In fact, in this model every single commit is like the top commit from a Pull Request. Every commit has a link to the code review that allowed the commit to land. You can see who wrote it and who reviewed it at a glance.

For clarity, let me describe the extreme case where you only commit to master. I'll outline things that are simpler because of this. I'm starting in order of least-important to most-important just to build the drama.

#### #1 Rebasing against master

With Pull Requests, if you want to catch up your local branch to master, you have to do the following:

1. Fetch the changes from remote
2. Rebase your branch on top of master
3. Merge any conflicts that arise

That doesn't sound so bad, but what about when you have a branch off a branch off of master? Then you have to repeat the last two steps for each branch, every time.

By contrast, if you only worked from master, you only have to do a `git pull --rebase` and you get to skip the cascading rebases, every time. You get to do just the work that you care about. All the branch jumping falls away without any cost. Might seem minor, but if you do the math on how often you have to do this, it adds up.

#### #2 Doing unrelated tasks

Many of us wear a lot of hats in our jobs. I'm the owner of a user-facing product codebase, which is many tens of thousands of lines, separated into dozens of features. That means I often jump between, for instance, refactoring big chunks of crufty old JavaScript (e.g. hundreds of lines of code across dozens of files) and working out small, nuanced bugs that relate to individual lines of code in a single file.

In the Pull Request world, this might mean I switch branches a dozen times per day. In most cases, that's not really necessary because many of these changes would never conflict. Yet, most highly productive people do half a dozen or more unrelated changes in day. This means that all that time spent branching and merging is wasted because those changes would never have conflicted anyway. This is evidenced by the fact that the majority of changes can be merged from the Github Pull Request UI without any manual steps at all. If the changes would never have conflicted, why are you wasting your time branching and merging? Surely you should be able to choose when/if to branch.

#### #3 Doing related tasks

One of the most time-destroying aspects of the Pull Request workflow is when you have multiple, dependent units of work. We all do this all the time. I want to achieve X, which requires doing V, W, X, and Y.

Sound far fetched? Well, just recently, I wanted to fix a user-facing feature. However, the UI code was all wrong. It needed to have a bunch of bad XHR code abstracted out first. Then, the UI code I wanted to change would be isolated enough to work on. The UI change required two server-side changes as well — one to alter the existing REST API and one to change the data representation. In order to properly test this, I'd need all three changes all together. But none of these changes required the same reviewer and they could all land independently, apart from the XHR and feature changes.

In the stacked diff world, this looks like this:

```
$ git log
commit c1e3cc829bcf05790241b997e81e678b3b309cc8 (HEAD -> master) 
Author: Jackson Gabbard <madeup@email.com>
Date:   Sat Sep 29 16:43:22 2018 +0100

    Alter API to enable my-sweet-feature-change

commit 6baac280353eb3c69056d90202bebef5de963afe
Author: Jackson Gabbard <madeup@email.com> Date: Sat Sep 29 16:44:27 2018 +0100

    Alter the database schema representation to enable my-sweet-feature 
commit a16589b0fec54a2503c18ef6ece50f63214fa553
Author: Jackson Gabbard <madeup@email.com>
Date:   Sat Sep 29 16:42:28 2018 +0100

    Make awesome user-facing change

commit cd2e43210bb48158a1c5eddb7c178070a8572e4d
Author: Jackson Gabbard <madeup@email.com>
Date:   Sat Sep 29 16:41:26 2018 +0100

    Add an XHR library to abstract redundant calls

commit 5c63f48334a5879fffee3a29bf12f6ecd1c6a1dc  (origin/master, origin/HEAD)
Author: Some Other Engineer <madeup-2@email.com>
Date:   Sat Sep 29 16:40:16 2018 +0100
    
    Did some work on some things
```

The equivalent of the Git configuration of this might look like this:

```
$ git log

commit 55c9fc3be10ebfe642b8d3ac3b30fa60a1710f0a (HEAD -> api-changes)
Author: Jackson Gabbard <madeup@email.com>
Date:   Sat Sep 29 17:02:48 2018 +0100

    Alter API to enable my-sweet-feature-change

commit b4dd1715cb47ace52bc773312544eb5da3b08038 (data-model-change)
Author: Jackson Gabbard <madeup@email.com>
Date: Sat Sep 29 17:03:25 2018 +0100

    Alter the database schema representation to enable my-sweet-feature

commit 532e86c9042b54c881c955b549634b81af6cdd2b (my-sweet-feature)
Author: Jackson Gabbard <madeup@email.com>
Date:   Sat Sep 29 17:02:02 2018 +0100

    Make awesome user-facing change

commit d2383f17db1692708ed854735caf72a88ee16e46 (xhr-changes)
Author: Jackson Gabbard <madeup@email.com>
Date:   Sat Sep 29 17:01:29 2018 +0100

    Add an XHR library to abstract out redundant calls

commit ba28b0c843a863719d0ac489b933add61303a141 (master)
Author: Some Other Engineer <madeup-2@email.com>
Date:   Sat Sep 29 17:00:56 2018 +0100

    Did some work on some things
```

Realistically though, in the Pull Request world, this commonly goes one of two ways:

1. You care massively about code quality so you diligently create a branch off of master for V, then a branch off of V for W, then a branch off of W for X, then a branch off of X for Y. You create a pull request for each one (as above).
2. You actually want to get work done so you create one big ass Pull Request that has commits for V, W, X, and Y.

In either case, someone loses.

For Case #1, what happens when someone requests changes to V? Simple, right? You make those changes in branch V and push them, updating your PR. Then you switch to W and rebase. Then you switch to X and rebase. Then you switch to Y and rebase. And when you're done, you go to the orthopedist to get a walker because you're **literally elderly** now. You've wasted your best years rebasing branches, but hey — the commit history is clean AF.

Importantly, woe be unto you if you happened to miss a branch rebase in the middle somewhere. This also means that when it comes time to commit, you have to remember which destination branch to select in the Github UI. If you mess that up and merge from X to W after W was merged to master, you've got an exciting, life-shortening mess to clean up. Yay!

For Case #2, everyone else loses because people just don't feel the same burden of quality per-commit in a PR. You don't have a test plan for every commit. You don't bother with good documentation on each individual commit, because you're thinking in terms of a PR.

In this case, when different reviewers request changes to the code for theses V and W, you just slap commits Y++ and Y++++ onto the end of the Pull Request to address the feedback across all of the commits. This means that the coherence of codebase goes down over time.

You can't intelligently squash merge the aspects of the various commits in the Pull Request that are actually related. The tool doesn't work that way so people don't work or think that way. I can't tell you the number of times I've seen the last two or three commits to a PR titled with "Addresses feedback" or "tweaks" and nothing else. Those commits tend to be among the sloppiest and least coherent. In the context of the PR, that \*seems\* fine, but when you fast-forward 6 months and you're trying to figure out why some code doesn't do what it's supposed to and all you have in a stack of 20 commits from a seemingly unrepated PR and the git blame shows that the offending line comes from a commit titled "nits" and nothing else and no other context, life is just harder.

#### #4 Doing multiple sets of related tasks

If you happen to be one of the rare engineers who is so productive that you work on multiple, distinct problems at the same time — you still probably want a branch per-thing, even in the stacked diff workflow. This likely means that you create a branch per-thing (i.e. per distinct problem), but that you put out multiple units of code for review on each branch.

For the mortals amongst us, let's imagine the case where an amazing engineer is working on three different hard problems at once. This engineer is working on three different strands of work, each of which require many commits and review by many different people. This person might generate conflicts between their branches, but they also are clever enough and productive enough to manage that. Let's assume that each of this person's branches includes an average of 5 or more units of code review in solving each of the 3 distinct problems.

In the Pull Request model, this means that person will have to create 3 branches off of master and then 5 branches-of-branches.  Alternatively, this person will create 3 Pull Requests, each of which is stacked 5 commits deep with this that only go together because of a very high level problem, not because it actually makes sense for code review. Those 5 commits may not require the same reviewer. Yet, the pull request model is going to put the onus on a single reviewer, because that's how the tool works.

The Stacked Diff model allows that amazing engineer to choose how/if to branch any commit. That person can decide if their work requires 3 branches and 15 units of code review or if their work requires 15 branches and 15 units of code review or something different.

This is more important than many people realize. Engineering managers know that allowing their most productive people to be as productive as possible amounts to big chunks of the team's total output. Why on earth would you saddle your most productive engineers with a process that eats away at their productivity?

## Thoughtless commits are bad commits

Every single commit that hits a codebase means more shit to trawl through trying to fix a production bug while your system is melting. Every merge commit. Every junk mid-PR commit that still doesn't build but kinda gets your change closer to working. Every time you smashed two or three extra things into the PR because it was too much bother to create a separate PR. These things add up. These things make a codebase harder to wrangle, month after month, engineer after engineer.

How do you git bisect a codebase where every 6th commit doesn't build because it was jammed into the middle of a Pull Request?

How much harder is it to audit a codebase where many times the blame is some massive merge commit?

How much more work is it to figure out what a commit actually does by reading the code because the blame commit message was "fixes bugs" and the pull request was 12 commits back?

The answer is \*a lot harder\*. Specifically because Pull Requests set you up for way more, way lower quality commits. It's just the default mode of the workflow. That is what happens in practice, in codebases all over the world, every day. I've seen it in five different companies now on two continents in massively different technical domains.

## Make the default mode a good one

You can make the argument that **none of this is the fault of Pull Requests**. Hi, thanks for your input. You're technically correct. To you, I'd like to offer the Tale of the Tree Icon. When Facebook re-launched Facebook Groups in 2011, I was the engineer who implemented the New User Experience. I worked directly with the designer who implemented the Group Icons, which show up in the left navigation of the site. Weeks after launch, we noticed that almost all the groups had their icon set to… a tree. It was a gorgeous icon designed by the truly exceptional [Soleio Cuervo](https://www.crunchbase.com/person/soleio-cuervo). But… a tree? Why?

### Because it was the first thing in the list.

People choose whatever is easiest. Defaults matter. So much. Even us demi-god-like Engineers are subject to the trappings of default behaviour. Which is why Pull Requests are terrible for code quality. The easiest behaviour is shoehorning in a bunch of shit under one PR because it's just so much work to get code out for review.

This is where Stacked Diffs win out, no question. It's not even close. The default behaviour is to be able to create a unit of code review for any change, no matter how minor. This means that you can get the dozens of uninteresting changes that come along with any significant work approved effortlessly. The changes that are actually controversial can be easily separated from the hum-drum, iterative code that we all write every day. Pull Requests encourage exactly the opposite — pounding in all of the changes into one high-level thesis and leaving the actual commit history a shambles.

## Coding as a queue

The fundamental shift that the Stacked Diff workflow enables is moving from the idea that every change is a branch of off master and to a world where your work is actually a queue of changes ahead of master. If you're a productive engineer, you'll pretty much always have five or more changes out for review. They'll get reviewed in some order and commited in some order. With Pull Requests, the work queue is hidden behind the cruft of juggling branches and trying to treat each change like a clean room separated from your other work. With Stacked Diffs, the queue is obvious — it's a stack of commits ahead of master.  You put new work on the end of the queue. Work that is ready to land gets bumped to the front of the queue and landed onto master. It's a much, much simpler mental model than a tangle of dependent branches and much more flexible than moving every change into the clean room of a new branch.

(For the pedantic few out there, yes, I just said stacked diffs are like a queue. Yeah… I didn't name the workflow. Don't hurl the rotten tomatoes at me.)

By now, you're probably sick of this theoretical/rhetorical discussion of what good engineering looks like. Let's switch gears and talk about this in practical, day to day terms.

## Case Study #1: The Highly Productive Coder

In this case study, we take a look at Suhair. Suhair is a really productive coder. Suhair produces 10 or more high quality commits every day.

### With Pull Requests

Suhair starts the day fixing a bug. Creates a branch, makes changes. Commits them. Suhair then pushes to the remote branch. Then navigates away from the terminal to the Github UI to create a pull request.

Next, Suhair switches back to master, pulls, and creates a new branch to work on a new feature. Commits code. This code is completely unrelated to the bug fix. In fact, they would never generate merge conflicts. Still, Suhair sticks to branches. Works on the feature. Gets it to a good RFC state. Suhair pushes the changes. In Github, Suhair creates a pull request.

Next Suhair starts working on another feature improvement. Switches to master. Pulls. Branches. But… uh oh. This change depends on his bug fix from earlier? What to do? He goes to the bug fix PR, sees if there are any comments. One person left some passing comments, but the person Suhair needs to review it hasn't commented.

So Suhair decides it's too much work to create a branch off his bug fix branch and decides to do something else in the interim. Suhair pings the needed person, begging for code review, interrupting their flow and then starts working on something else.

### With Stacked Diffs

Suhair pulls master in the morning to get the latest changes. Makes the first bug fix, commits it, creates a Diff to be reviewed, entirely from the command line. Suhair then works on the unrelated feature. Commits. Creates a Diff from the command line. Then starts working on the bug-fix-dependent feature improvement. Because Suhair never left master, the bug fix is still in the stack. So, Suhair can proceed with the feature improvement uninterrupted. So, Suhair does the work. Commits it. Creates a Diff for review.

By now, the person who should have reviewed the initial bug fix actually got around to it. They give Suhair some feedback which Suhair incorporates via [interactive rebase](https://git-scm.com/book/en/v2/Git-Tools-Rewriting-History). Suhair rebases the changes on top of the updated bug fix, which generates a small merge conflict with the feature improvement, which Suhair fixes. Then Suhair lands the change via interactive rebase. On the next `git pull –rebase` against remote master, the local commit disappears because remote master already has an identical change, and Suhair's queue of commits ahead of master decreases by one.

As a bonus for Suhair today, the same reviewer who approved the bug fix is also the reviewer needed for his feature improvement. That person approved his tweaks right after they reviewed his bug fix. So, Suhair rebases those changes to be at the top of the commit stack, then lands them. Suhair never switches branches. At the end of the day, only the feature work is left in his local repo, everything else is landed on top of master.

The next day, Suhair comes in, runs `git pull –rebase` and starts working without any branch juggling.

## Case Study #2: The Free Spirited Hacker

Charlie is a productive, energetic, somewhat amoral hacker who just wants to get work done as fast as possible. Charlie knows the product better than any one, but doesn't really care about code quality. Charlie is best paired with a senior tech lead (or two) who can rein in the chaos a bit.

### With Pull Requests

Charlie starts the day by branching master and spamming the branch with five commits that are only vaguely related. Charlie's commits are big, chunky commits that don't make a lot of sense. They tend to be a bunch of things all crammed together. Reviewers of Charlie's code always know they'll have a lot of work ahead of them to make sense of the tangle of ideas. Because of this, they tend to put off reviewing. Today, a senior tech lead takes 45 minutes to read through all these changes, giving detailed feedback and explaining how to improve the various strands of the change. Charlie commits more changes onto the PR, addressing feedback and also makes random "fixes" along the way. In the end, the PR is probably okay, but it's certainly not coherent and may the Mighty Lobster on High protect those who have to make sense of the code in the coming months.

During this laborious back-and-forth, Charlie's best option is to keep piling things on this PR because all the related changes are in it. The tech lead doesn't have a reasonable alternative to offer Charlie.

### With Stacked Diffs

Charlie blasts out five commits and five Diffs back to back. Each one addresses something specific. Each one goes to a different reviewer because Charlie happens to be making a sweeping change to the codebase. Charlie knows how it all fits together and the tech leads can make sure that the individual changes aren't going to ruin everything.

Because the changes are smaller and more coherent, they get much better review. A tech lead points out that one of the changes is clearly two separate theses that happen to touch the same set of files. This tech lead reviewing the code pushes back on Charlie. The tech lead points out that these should actually be two separate commits. Unfazed, Charlie abandons the Diff. Using interactive rebase to rewind history to that troublesome commit, Charlie uses `git reset` to uncommit the single commit that has two theses.

At this point, Charlie's local master is two commits ahead of remote master and has a bag of uncommitted changes that Charlie is currently hacking on. There are two more changes that are in the future, waiting to be added back to the local commit history by Git when Charlie is done rebasing interactively.

So, Charlie uses `git add -p` to separate out one change from the other and creates two new commits and two new diffs for them separately. They each get a title, a description, and a test plan. Charlie then runs `git rebase –continue` to bring fast-forward time and bring back the later changes. Now, Charlie's local master is six commits ahead of remote master. There are six Diffs out for review. Charlie never switched branches.

## Case Study #3: The Engineer with a Bad Neighbour

Yang is a great engineer working in a fun part of the infrastructure. Unfortunately, Yang has a bad neighbour. This other engineer constantly lands the team in trouble. Today, Yang has found that the build is broken due to yet another incomprehensible change. The neighbour has a "fix" out for a review, but no one trusts it and several knowledgeable people are picking through the code in a very contentious code review. Yang just wants to get work done, but can't because the bug is blocking everything.

### With Pull Requests

Yang will checkout the remote branch with the "fix". Next, Yang will branch off of that branch in order to get a sort-of-working codebase. Yang gets to work. Midday, the bad neighbour pushes a big update to the "fix". Yang has to switch to that branch, pull, then switch back to the branch Yang has been working on, rebase, and then push the branch for review. Yang then switches gears to refactor a class nearby in the codebase. So, Yang has to go back to the bug "fix" branch, branch off it, start the refactor, and push the commit remotely for review. The next day, Yang wants to merge the changes, but the "fix" has changed and needs rebasing again. Yang switches to the bug fix branch, pulls. Switches to the first branch, rebases. Pushes. Switches to GitHub to do the merge, carefully selecting to merge onto master rather than the bug fix branch. Then Yang goes back to the terminal, switches to the second feature, rebases, pushes, goes to GitHub, selecrs to merge to master, and merges. Then, Yang applies for AARP, because Yang is now in geriatric care.

### With Stacked Diffs

Yang sees that the Diff for the "fix" is out for review. Yang uses the Phabricator command line tool to patch that commit on top of master. This means that it's not a branch. It's just a throwaway local commit. Yang then starts working on the first change. Yang submits a Diff for review from the command line. Later, the "fix" has changed, so Yang drops the patch of the old version from the Git history and patches in the updated one via interactive rebase. Yang then starts working on the second change, submits a Diff for review. The next day, Yang is ready to land both changes. First, Yang dumps the previous patch of the fix and repatches the update to make sure everything works. Then, Yang uses the command line via interactive rebase to land both of the changes without ever switching branches or leaving the terminal. Later, the fix lands, so Yang does a  got pull –rebase and the local patch falls off because it's already in master. Then Yang goes to skydiving because Yang is still young and vital.

## In Conclusion

As you can see from the Case Studies, you can definitely get good work done no matter what tool chain you use. I think it's also quite clear that Stacked Diffs make life easier and work faster. Many engineers reading this will say the cost of switching is too high. This is expectable. It's a thing called the [Sunk Cost Fallacy](https://youarenotsosmart.com/2011/03/25/the-sunk-cost-fallacy/). Everyone prefers the thing they feel they have invested in, even if there is an alternative that is provably more valuable. The stacked diff workflow is a clearly higher-throughput workflow that gives significantly more power to engineers to develop code as they see fit.

Inside Facebook, engineering used the branch-oriented workflow for years. They eventually replaced it with the stacked diff workflow because it made engineers more productive in very concrete terms. It also encourages good engineering practices in a way exactly opposite to branching and Pull Requests.

Something I haven't touched on at all is the actual work of reviewing code. As it turns out, Phabricator also happens to offer better code review tools, but I'll save that for another post.

