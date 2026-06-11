Title: [转] Design Patterns Suck
Date: 2026-06-11 09:26:04
Category: 编程
Tags: 转载, programming
CommentId: X

原文作者: Kirill Bobrov

原文链接: [https://luminousmen.com/post/design-patterns-suck/](https://luminousmen.com/post/design-patterns-suck/)

为防遗失，转载一份。

<!-- PELICAN_END_SUMMARY -->

In software engineering, the term "design pattern" (which, honestly, is kind of redundant — aren't all patterns designs?) gets thrown around a lot. It originally came from architecture — actual architecture, with buildings and floorplans — not software.

But in 1994, the software world got its own version when the now-infamous book"Design Patterns" was published by Gamma, Helm, Johnson, and Vlissides — aka the "Gang of Four" (GoF). They introduced 23 canonical patterns as higher-level abstractions than function calls. These patterns were meant to be language-agnostic, reusable templates for solving recurring software design problems.

Sounds nice, right? Almost too nice...

The problem is that design patterns have been elevated from useful vocabulary into something closer to dogma. They're taught as universal solutions, applied where they aren't needed, and treated as a mark of good engineering.

The reality is: **Design patterns suck.**

Yeah, I said it.

**Design patterns are overrated, overused, and often flat-out unnecessary.**

That might sound harsh, especially those of you who keep their Gang of Four books near their bedsides, but hear me out. Most of the time, design patterns are nothing but ugly workarounds for the fact that our programming languages aren't powerful enough or flexible enough to express what we actually want.

## Java and Its Love Affair with Boilerplate

Take Java, for example (I'll be bashing Java quite a bit today, so get comfortable). Where do we even start? Java is the poster child for "design-pattern-mania". Every single project looks like a carbon copy of itself because Java developers are taught to just dump in as many patterns as possible.

It's the language that practically forced design patterns into mainstream use. Why? Because Java is verbose, stiff, and lacks expressiveness. It's like writing a novel where you're only allowed to use three-syllable words — every problem feels ten times harder than it has to be.

*Oh, you're working on a simple CRUD app?* Better throw in a Factory, maybe an Observer for that database change notification, and don't forget the Singleton — because, y'know, we all need a global logger, right?

💡 Singleton is a pattern that is 95% used for logging and 5% for creating problems in concurrent apps.

## Pattern vs Language Feature

The crux of why design patterns are often garbage is that most of the time they exist only because the language itself is missing some capability. You're basically doing workarounds for language limitations.

Take the Singleton pattern as an example. You've seen this a thousand times:

```java
public class Logger {

    private static Logger instance;

    private Logger() {}

    public static Logger getInstance() {
        if (instance == null) {
            instance = new Logger();
        }
        return instance;
    }
}
```

That's like 15 lines of code just to say, "I want only one instance of this thing". What are we, cavemen? We shouldn't need to hand-write this kind of thing. A modern language should provide constructs to handle this elegantly, but nope, not Java. Instead, we get tons of boilerplate and complexity masquerading as "best practices".

Want to see how Scala handles it?

```scala
object Logger
```

That's it. That's the entire Singleton pattern. Done.

No need to mess around with static blocks, thread safety, or lazy instantiation nonsense. Scala does what Java should have done in the first place: treat this as a basic language feature, not a pattern you need to manually enforce. Java forces you into this mess because it doesn't have first-class functions. It's the language's fault, not yours, that you're writing a Strategy pattern.

Design patterns aren't solving problems with your code; they're solving problems with your language.

A Factory pattern? That's just Java's refusal to give you proper constructors or a way to handle complex object creation natively. In languages like Python, Ruby, or Scala, you rarely need a Factory. In fact, most of the design patterns Java developers go on about just vanish in more flexible, expressive languages.

Take Python for example:

- Need a Factory? Just pass a function or use `__init__` smartly.
- Want a Singleton? Throw in a module or a class that you initialize once, and call it a day.
- Observer? Well, functions are first-class citizens. Just pass them around.

The fact is, in a language that's expressive enough, patterns either become trivial or, better yet, they just don't exist. You handle the problems directly, not by wrapping them in abstractions that someone else cooked up 20 years ago in a language that hasn't aged well.

💡 In Lisp, you can override the behavior of any construct. Patterns didn't take root there at all — you just write a macro, and the language bends to you.

## The Cult of Overengineering

![design_patterns_suck_1](/images/2026/design-patterns-suck-p1.png)

Design patterns also feed into a deeper problem in the software world: overengineering. I've seen junior engineers (and some senior ones, unfortunately) who get this wide-eyed look when they hear "design patterns" and immediately try to shoehorn as many as possible into their project.

They're solving imaginary problems.

When this happens, the codebase goes from something understandable to something unreadable, fragile, and overly abstracted. It becomes a labyrinth of interfaces, factory methods, and weird naming conventions that make you feel like you're trying to interpret ancient texts.

💡 You know how you know you're writing in Java? When 80% of the files in the repository are interfaces that implement interfaces that do nothing but throw the call further away.

"Good" design patterns tend to be over-engineered because they are required to cater to as many use cases as possible. Over-engineered code has a cost though: you have to read it, understand what it does, and understand how it works within the context of the entire software system. Consequently, as with any other software development technique, you have to evaluate the technique against the cost of using the technique, and decide if the benefits exceed the cost.

Not every problem needs a design pattern. In fact, most problems don't. Often the simplest, most straightforward solution is the right one. As a rule of thumb, if your solution needs a diagram to explain it, you've gone too far.

## Where Patterns are Actually Useful

The most honest value of patterns: giving a short name to a big idea. In a team, it's easier to say "that's a facade" than to explain every time why we're hiding three classes behind one wrapper.

That's it. That's the real use case.

Patterns aren't for teaching you to write good code. They're for talking about code that's already written. So you can ask "what's this class?" and hear "oh, that's part of the mediator". Not for frantically comparing your code to UML diagrams going "which pattern do I apply here?!"

A developer who understands the underlying concepts — separation of concerns, encapsulation, composition over inheritance — will write clean code naturally, even if they've never heard the word "Singleton". The patterns are just labels for what good developers already know how to do.

I've worked at several of the biggest tech companies. Nobody uses these terms day to day, and I've never once been asked about them in an interview (it would be a red flag for me).

## The Gosling Philosophy vs The Guido Philosophy

There's a [great bit from DHH](https://youtube.com/watch?v=vagyIcmIGOQ&t=3264) that nails why Java ended up this way.

James Gosling, the designer of Java, had a dark view of programmers. His premise: the average developer is going to shoot themselves in the foot if you give them too much power. So Java was built as a sandbox — keep it rigid, keep it safe, don't let them hurt themselves. Great for a mid-tier insurance company writing code that has to last 20 years. Not so great for expressiveness.

Guido van Rossum went the opposite direction with Python. His premise: code is read more than it's written, so optimize for clarity and give programmers real tools. First-class functions, decorators, context managers, duck typing — Python gives you the building blocks to solve problems directly instead of routing everything through class hierarchies and interface ceremonies.

Design patterns are a Gosling-world solution. They exist because the language doesn't trust you to solve the problem directly. In a Guido-world language, you just... solve it.

Design patterns are relics of a time when languages weren't expressive enough. The fact that half of the GoF patterns disappear in Python, Ruby, or Scala tells you everything — they were never about design. They were about the language getting out of your way.

