/**
 * Built-in real reference experiment sessions for immediate evaluation in Phase 9.
 * Sourced directly from verified Ollama llama3.2:3b runs.
 */

export const REFERENCE_SESSIONS = [
  {
    id: 'ref-few-shot-recursion',
    title: 'Few-Shot: Recursion in Java (llama3.2:3b)',
    topic: 'Explain recursion in Java',
    strategy: 'few_shot',
    model: 'llama3.2:3b',
    context: {
      knowledge_level: 'beginner',
      learning_goal: 'concept_understanding',
      available_time: '30_minutes',
      explanation_style: 'step_by_step',
      difficulty: 'easy',
      output_type: 'explanation',
    },
    response: {
      title: 'Understanding Recursion in Java',
      learning_objectives: [
        'Define recursion and its importance in programming',
        'Understand the concept of base case and recursion depth',
        'Learn to implement recursion in Java',
      ],
      concept_explanation:
        'Recursion is a programming technique where a function calls itself until a base case is met. This allows the function to solve problems by breaking them down into smaller sub-problems of the same type. Recursion is useful for solving problems that have a recursive structure, such as tree or graph traversal.',
      topic_breakdown: [
        {
          heading: 'What is Recursion?',
          content: 'Recursion is a programming technique where a function calls itself until a base case is met.',
        },
        {
          heading: 'How Does Recursion Work?',
          content:
            'Recursion works by breaking down a problem into smaller sub-problems of the same type. The function solves each sub-problem and then solves the next one until a base case is met.',
        },
      ],
      examples: [
        {
          title: 'Recursive Fibonacci Function',
          code: 'public int fibonacci(int n) {\n  if (n <= 1) return n;\n  return fibonacci(n-1) + fibonacci(n-2);\n}',
          explanation: 'This function uses recursion to calculate the Fibonacci sequence.',
        },
      ],
      analogy:
        'Think of recursion like a Russian nesting doll. Each call to the function is like opening a new doll, and the function solves the problem by opening the next doll until the base case is met.',
      practice_questions: [
        'What is the difference between recursive and iterative solutions to a problem?',
        'How do you avoid stack overflow errors in recursive functions?',
      ],
      quiz: [
        {
          question: 'What is the base case in a recursive function?',
          options: [
            'The largest sub-problem',
            'The smallest sub-problem',
            'A problem that can be solved directly',
            'A problem that is undefined',
          ],
          correct_index: 2,
          explanation: 'The base case is a problem that can be solved directly without calling the function again.',
        },
      ],
      revision_checklist: [
        'I can define recursion and its importance in programming.',
        'I can explain the concept of base case and recursion depth.',
      ],
    },
  },
  {
    id: 'ref-zero-shot-recursion',
    title: 'Zero-Shot: Recursion in Java (llama3.2:3b)',
    topic: 'Explain recursion in Java',
    strategy: 'zero_shot',
    model: 'llama3.2:3b',
    context: {
      knowledge_level: 'beginner',
      learning_goal: 'concept_understanding',
      available_time: '30_minutes',
      explanation_style: 'step_by_step',
      difficulty: 'easy',
      output_type: 'explanation',
    },
    response: {
      title: 'Understanding Recursion in Java',
      learning_objectives: [
        'Define recursion and its importance in programming',
        'Understand the basic structure of a recursive function in Java',
        'Identify the conditions for a recursive function to terminate',
      ],
      concept_explanation:
        'Recursion is a programming technique where a function calls itself repeatedly until it reaches a base case that stops the recursion. This process allows a function to solve problems that have a recursive structure, like tree traversals or sorting algorithms.',
      topic_breakdown: [
        {
          heading: 'What is Recursion?',
          content:
            'Recursion is a programming technique where a function calls itself repeatedly until it reaches a base case that stops the recursion.',
        },
        {
          heading: 'How Does Recursion Work?',
          content:
            'A recursive function calls itself with a smaller input until it reaches a base case that stops the recursion.',
        },
        {
          heading: 'Conditions for Recursion to Terminate',
          content:
            'A recursive function must have a base case that stops the recursion and a clear definition of the problem being solved.',
        },
      ],
      examples: [
        {
          title: 'Factorial Function',
          code: 'public int factorial(int n) {\n  if (n == 0) return 1;\n  else return n * factorial(n - 1);\n}',
          explanation:
            'This is a simple example of a recursive function that calculates the factorial of a number.',
        },
      ],
      analogy:
        'A recursive function is like a tree: it branches out into smaller sub-problems, solves each sub-problem, and then combines the solutions to form the final answer.',
      practice_questions: [
        'What is the base case for the factorial function?',
        'How does the recursive function call itself in the factorial example?',
      ],
      quiz: [
        {
          question: 'What is the primary advantage of using recursion in programming?',
          options: [
            'A) Efficient use of memory',
            'B) Easy to implement',
            'C) Can solve complex problems',
            'D) Fast execution time',
          ],
          correct_index: 2,
          explanation:
            'Recursion can solve complex problems that have a recursive structure, like tree traversals or sorting algorithms.',
        },
      ],
      revision_checklist: [
        'Recursion is a programming technique where a function calls itself repeatedly until it reaches a base case.',
        'Identify the base case and the recursive call in a recursive function.',
        'Understand the conditions for a recursive function to terminate.',
      ],
    },
  },
]
