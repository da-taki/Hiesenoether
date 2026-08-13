# Results

Across the 13 normal tasks, GPT-5.6 Sol produced 12 behavior-preserved candidates, 0 manually verified semantic divergences, 0 silent semantic divergences, and 1 ordinary programming bug caught by ordinary tests.

Across the 13 warned tasks, GPT-5.6 Sol produced 11 behavior-preserved candidates, 0 manually verified semantic divergences, 0 silent semantic divergences, and 2 ordinary programming bugs caught by ordinary tests.

Self-assessment was conservative. Normal: 3 YES, 10 NO, 0 false YES, 9 behavior-preserved NO claims. Warned: 4 YES, 9 NO, 0 false YES, 7 behavior-preserved NO claims.

Semantic paired analysis: `normal preserved / warned preserved` = 13, with all other semantic-divergence pair categories at 0. Behavior-level ordinary bugs occurred in Markdown in both conditions and BeautifulSoup in the warned condition.
