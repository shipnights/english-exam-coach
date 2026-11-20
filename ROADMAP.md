# Roadmap

What I plan to build, roughly in this order. It is a plan, not a promise, and the order will move
as I learn what helps most when practising. Each open item is also a GitHub issue with a rough
hour estimate.

## Next: make the writing loop better

- [ ] Add your own prompts from a JSON file, so the bank is not limited to the twelve in the repo
- [ ] Redo flow: rewrite your answer after reading the feedback and compare the two attempts
- [ ] Mistake log: keep the recurring problems the feedback finds and show them before each task
- [ ] Progress charts for estimated range and word count over time, and a CSV export

## Trust in the scores

- [ ] A `consistency` command that scores the same response several times and reports the spread,
      so I can see how stable the estimates are before relying on them
- [ ] A small set of reference responses written for the repo, used to check that scores move in
      the right direction as quality changes
- [ ] Show the criteria wording the model was given, next to each score

## More skills

- [ ] Reading practice with original passages and questions
- [ ] Speaking and listening practice: first decide an approach that keeps the app local-first and
      does not send audio to third parties by default, then reuse the same feedback pipeline

## Packaging and quality

- [x] GitHub Actions workflow that runs the test suite on Python 3.11 and 3.12
- [ ] One-command start on Windows and a `pipx` install
- [ ] Accessibility pass: keyboard use, focus order, contrast and screen reader labels
- [ ] Browser tests for the writing page timer and word count

## Not planned

Accounts, hosting, payments and sharing other people's work. This stays a personal tool that runs
on your own machine.
