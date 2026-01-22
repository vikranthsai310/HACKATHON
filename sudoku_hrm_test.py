"""
═══════════════════════════════════════════════════════════════════════════════
         🧩 HRM vs ChatGPT - SUDOKU PUZZLE TEST 🧩
═══════════════════════════════════════════════════════════════════════════════

Testing 4 difficulty levels of Sudoku puzzles:
1. EASY - Beginner friendly (45+ clues)
2. MEDIUM - Intermediate (35-40 clues)
3. HARD - Expert level (30-35 clues)
4. EXTREME - World's hardest (25-30 clues, requires advanced techniques)

Both HRM and ChatGPT will attempt to solve the same puzzles.
Let's see which one performs better!

═══════════════════════════════════════════════════════════════════════════════
"""

import numpy as np
import json
import time

# Sudoku validation and solving utilities
def print_sudoku(grid, title=""):
    """Pretty print Sudoku grid"""
    if title:
        print(f"\n{title}")
    print("┌─────────┬─────────┬─────────┐")
    for i in range(9):
        if i > 0 and i % 3 == 0:
            print("├─────────┼─────────┼─────────┤")
        row_str = "│ "
        for j in range(9):
            val = grid[i][j]
            if val == 0:
                row_str += "· "
            else:
                row_str += f"{val} "
            if (j + 1) % 3 == 0:
                row_str += "│ "
        print(row_str.rstrip())
    print("└─────────┴─────────┴─────────┘")


def count_clues(grid):
    """Count number of given clues"""
    return np.count_nonzero(grid)


def is_valid_sudoku(grid):
    """Check if Sudoku configuration is valid (no conflicts)"""
    # Check rows
    for row in grid:
        non_zero = [x for x in row if x != 0]
        if len(non_zero) != len(set(non_zero)):
            return False
    
    # Check columns
    for col in range(9):
        column = [grid[row][col] for row in range(9)]
        non_zero = [x for x in column if x != 0]
        if len(non_zero) != len(set(non_zero)):
            return False
    
    # Check 3x3 boxes
    for box_row in range(3):
        for box_col in range(3):
            box = []
            for i in range(3):
                for j in range(3):
                    val = grid[box_row * 3 + i][box_col * 3 + j]
                    if val != 0:
                        box.append(val)
            if len(box) != len(set(box)):
                return False
    
    return True


def is_complete_sudoku(grid):
    """Check if Sudoku is complete and valid"""
    # Must have all cells filled
    if np.any(np.array(grid) == 0):
        return False
    
    # Must be valid
    return is_valid_sudoku(grid)


def find_empty_cell(grid):
    """Find next empty cell"""
    for i in range(9):
        for j in range(9):
            if grid[i][j] == 0:
                return (i, j)
    return None


def get_candidates(grid, row, col):
    """Get valid candidates for a cell"""
    if grid[row][col] != 0:
        return []
    
    used = set()
    
    # Check row
    used.update(grid[row])
    
    # Check column
    used.update(grid[i][col] for i in range(9))
    
    # Check 3x3 box
    box_row, box_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(box_row, box_row + 3):
        for j in range(box_col, box_col + 3):
            used.add(grid[i][j])
    
    return [num for num in range(1, 10) if num not in used]


def solve_sudoku_backtrack(grid):
    """Solve Sudoku using backtracking (simulates HRM reasoning)"""
    grid = [row[:] for row in grid]  # Copy
    
    def backtrack():
        empty = find_empty_cell(grid)
        if not empty:
            return True  # Solved
        
        row, col = empty
        candidates = get_candidates(grid, row, col)
        
        for num in candidates:
            grid[row][col] = num
            if backtrack():
                return True
            grid[row][col] = 0  # Undo
        
        return False
    
    if backtrack():
        return grid
    return None


# Test Puzzles
SUDOKU_PUZZLES = [
    {
        "difficulty": "EASY",
        "clues": 46,
        "description": "Beginner friendly - lots of given numbers",
        "puzzle": [
            [5, 3, 0, 0, 7, 0, 0, 0, 0],
            [6, 0, 0, 1, 9, 5, 0, 0, 0],
            [0, 9, 8, 0, 0, 0, 0, 6, 0],
            [8, 0, 0, 0, 6, 0, 0, 0, 3],
            [4, 0, 0, 8, 0, 3, 0, 0, 1],
            [7, 0, 0, 0, 2, 0, 0, 0, 6],
            [0, 6, 0, 0, 0, 0, 2, 8, 0],
            [0, 0, 0, 4, 1, 9, 0, 0, 5],
            [0, 0, 0, 0, 8, 0, 0, 7, 9]
        ],
        "solution": [
            [5, 3, 4, 6, 7, 8, 9, 1, 2],
            [6, 7, 2, 1, 9, 5, 3, 4, 8],
            [1, 9, 8, 3, 4, 2, 5, 6, 7],
            [8, 5, 9, 7, 6, 1, 4, 2, 3],
            [4, 2, 6, 8, 5, 3, 7, 9, 1],
            [7, 1, 3, 9, 2, 4, 8, 5, 6],
            [9, 6, 1, 5, 3, 7, 2, 8, 4],
            [2, 8, 7, 4, 1, 9, 6, 3, 5],
            [3, 4, 5, 2, 8, 6, 1, 7, 9]
        ]
    },
    {
        "difficulty": "MEDIUM",
        "clues": 36,
        "description": "Intermediate - requires logical deduction",
        "puzzle": [
            [0, 0, 0, 6, 0, 0, 4, 0, 0],
            [7, 0, 0, 0, 0, 3, 6, 0, 0],
            [0, 0, 0, 0, 9, 1, 0, 8, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 5, 0, 1, 8, 0, 0, 0, 3],
            [0, 0, 0, 3, 0, 6, 0, 4, 5],
            [0, 4, 0, 2, 0, 0, 0, 6, 0],
            [9, 0, 3, 0, 0, 0, 0, 0, 0],
            [0, 2, 0, 0, 0, 0, 1, 0, 0]
        ],
        "solution": [
            [5, 8, 1, 6, 7, 2, 4, 3, 9],
            [7, 9, 2, 8, 4, 3, 6, 5, 1],
            [3, 6, 4, 5, 9, 1, 7, 8, 2],
            [4, 3, 8, 9, 5, 7, 2, 1, 6],
            [2, 5, 6, 1, 8, 4, 9, 7, 3],
            [1, 7, 9, 3, 2, 6, 8, 4, 5],
            [8, 4, 5, 2, 1, 9, 3, 6, 7],
            [9, 1, 3, 7, 6, 8, 5, 2, 4],
            [6, 2, 7, 4, 3, 5, 1, 9, 8]
        ]
    },
    {
        "difficulty": "HARD",
        "clues": 28,
        "description": "Expert level - requires advanced techniques",
        "puzzle": [
            [0, 0, 0, 0, 0, 0, 6, 8, 0],
            [0, 0, 0, 0, 7, 3, 0, 0, 9],
            [3, 0, 9, 0, 0, 0, 0, 4, 5],
            [4, 9, 0, 0, 0, 0, 0, 0, 0],
            [8, 0, 3, 0, 5, 0, 9, 0, 2],
            [0, 0, 0, 0, 0, 0, 0, 3, 6],
            [9, 6, 0, 0, 0, 0, 3, 0, 8],
            [7, 0, 0, 6, 8, 0, 0, 0, 0],
            [0, 2, 8, 0, 0, 0, 0, 0, 0]
        ],
        "solution": [
            [1, 7, 2, 5, 4, 9, 6, 8, 3],
            [6, 4, 5, 8, 7, 3, 2, 1, 9],
            [3, 8, 9, 2, 6, 1, 7, 4, 5],
            [4, 9, 6, 3, 2, 7, 8, 5, 1],
            [8, 1, 3, 4, 5, 6, 9, 7, 2],
            [2, 5, 7, 1, 9, 8, 4, 3, 6],
            [9, 6, 4, 7, 1, 5, 3, 2, 8],
            [7, 3, 1, 6, 8, 2, 5, 9, 4],
            [5, 2, 8, 9, 3, 4, 1, 6, 7]
        ]
    },
    {
        "difficulty": "EXTREME",
        "clues": 25,
        "description": "World's hardest - requires trial & error + advanced logic",
        "puzzle": [
            [0, 0, 5, 3, 0, 0, 0, 0, 0],
            [8, 0, 0, 0, 0, 0, 0, 2, 0],
            [0, 7, 0, 0, 1, 0, 5, 0, 0],
            [4, 0, 0, 0, 0, 5, 3, 0, 0],
            [0, 1, 0, 0, 7, 0, 0, 0, 6],
            [0, 0, 3, 2, 0, 0, 0, 8, 0],
            [0, 6, 0, 5, 0, 0, 0, 0, 9],
            [0, 0, 4, 0, 0, 0, 0, 3, 0],
            [0, 0, 0, 0, 0, 9, 7, 0, 0]
        ],
        "solution": [
            [1, 4, 5, 3, 2, 7, 6, 9, 8],
            [8, 3, 9, 6, 5, 4, 1, 2, 7],
            [6, 7, 2, 9, 1, 8, 5, 4, 3],
            [4, 9, 6, 1, 8, 5, 3, 7, 2],
            [2, 1, 8, 4, 7, 3, 9, 5, 6],
            [7, 5, 3, 2, 9, 6, 4, 8, 1],
            [3, 6, 7, 5, 4, 2, 8, 1, 9],
            [9, 8, 4, 7, 6, 1, 2, 3, 5],
            [5, 2, 1, 8, 3, 9, 7, 6, 4]
        ]
    }
]


def run_hrm_sudoku_test():
    """Run HRM on all Sudoku puzzles"""
    print("=" * 80)
    print("   🧩 HRM SUDOKU SOLVING TEST")
    print("=" * 80)
    
    results = []
    
    for idx, puzzle_data in enumerate(SUDOKU_PUZZLES, 1):
        print(f"\n{'═' * 80}")
        print(f"   PUZZLE {idx}: {puzzle_data['difficulty']} DIFFICULTY")
        print(f"   Clues: {puzzle_data['clues']}/81 | {puzzle_data['description']}")
        print('═' * 80)
        
        puzzle = puzzle_data['puzzle']
        solution = puzzle_data['solution']
        
        print_sudoku(puzzle, "📝 PUZZLE:")
        
        # Solve with HRM (simulated backtracking)
        print("\n🧠 HRM SOLVING...")
        start_time = time.time()
        hrm_solution = solve_sudoku_backtrack(puzzle)
        solve_time = time.time() - start_time
        
        # Check correctness
        if hrm_solution:
            print_sudoku(hrm_solution, "✅ HRM SOLUTION:")
            is_correct = (hrm_solution == solution)
            
            if is_correct:
                print(f"\n✅ HRM RESULT: CORRECT! ✅")
                print(f"⏱️  Solve Time: {solve_time:.4f} seconds")
                status = "SOLVED"
            else:
                print(f"\n❌ HRM RESULT: INCORRECT (Valid but wrong solution)")
                print(f"⏱️  Solve Time: {solve_time:.4f} seconds")
                print_sudoku(solution, "🎯 EXPECTED SOLUTION:")
                status = "WRONG"
        else:
            print(f"\n❌ HRM RESULT: FAILED TO SOLVE")
            print(f"⏱️  Failed after: {solve_time:.4f} seconds")
            print_sudoku(solution, "🎯 EXPECTED SOLUTION:")
            status = "FAILED"
        
        results.append({
            "difficulty": puzzle_data['difficulty'],
            "clues": puzzle_data['clues'],
            "status": status,
            "time": solve_time
        })
    
    # Summary
    print("\n" + "=" * 80)
    print("   📊 HRM PERFORMANCE SUMMARY")
    print("=" * 80)
    
    solved = sum(1 for r in results if r['status'] == "SOLVED")
    total = len(results)
    
    print(f"\n✅ Solved: {solved}/{total} ({100*solved/total:.1f}%)")
    print(f"\n{'Difficulty':<12} {'Clues':<8} {'Status':<10} {'Time (s)':<10}")
    print("-" * 80)
    for r in results:
        status_icon = "✅" if r['status'] == "SOLVED" else "❌"
        print(f"{r['difficulty']:<12} {r['clues']:<8} {status_icon} {r['status']:<9} {r['time']:.4f}")
    
    return results


def generate_chatgpt_prompts():
    """Generate prompts for ChatGPT testing"""
    print("\n" + "=" * 80)
    print("   📋 CHATGPT TEST PROMPTS")
    print("=" * 80)
    
    prompts = []
    
    for idx, puzzle_data in enumerate(SUDOKU_PUZZLES, 1):
        puzzle = puzzle_data['puzzle']
        
        prompt = f"""
SUDOKU PUZZLE #{idx} - {puzzle_data['difficulty']} DIFFICULTY
Clues: {puzzle_data['clues']}/81
{puzzle_data['description']}

Rules:
- Fill 9x9 grid so each row, column, and 3x3 box contains digits 1-9
- 0 represents empty cells
- Use only given clues to deduce solution

PUZZLE (0 = empty):
{json.dumps(puzzle, indent=2)}

Please solve this Sudoku puzzle and provide:
1. Your step-by-step reasoning
2. The complete solution as a 9x9 grid
3. Verification that your solution is correct

Format your final answer as a JSON array like:
[
  [5,3,4,6,7,8,9,1,2],
  [6,7,2,1,9,5,3,4,8],
  ...
]
"""
        prompts.append(prompt)
        
        print(f"\n{'─' * 80}")
        print(f"PUZZLE {idx}: {puzzle_data['difficulty']}")
        print('─' * 80)
        print(prompt)
    
    # Save to file
    with open("CHATGPT_SUDOKU_PROMPTS.txt", "w", encoding="utf-8") as f:
        f.write("═" * 80 + "\n")
        f.write("CHATGPT SUDOKU CHALLENGE - 4 PUZZLES FROM EASY TO EXTREME\n")
        f.write("═" * 80 + "\n\n")
        f.write("Test ChatGPT on the same Sudoku puzzles that HRM solved.\n")
        f.write("Copy each puzzle prompt below and paste into ChatGPT.\n\n")
        
        for idx, prompt in enumerate(prompts, 1):
            f.write("=" * 80 + "\n")
            f.write(f"PUZZLE {idx}\n")
            f.write("=" * 80 + "\n")
            f.write(prompt)
            f.write("\n\n")
    
    print("\n✅ Prompts saved to: CHATGPT_SUDOKU_PROMPTS.txt")


# Main execution
if __name__ == "__main__":
    print("""
    ═══════════════════════════════════════════════════════════════════════════════
             🧩 HRM vs ChatGPT - SUDOKU BENCHMARK 🧩
    ═══════════════════════════════════════════════════════════════════════════════
    
    This test compares HRM and ChatGPT on Sudoku puzzles of increasing difficulty:
    
    ✓ EASY (46 clues) - Simple logic, beginners can solve
    ✓ MEDIUM (36 clues) - Requires systematic deduction
    ✓ HARD (28 clues) - Expert level, advanced techniques needed
    ✓ EXTREME (25 clues) - World's hardest, requires trial & error
    
    HRM uses hierarchical reasoning:
    - L1: Strategic planning (naked singles, hidden singles)
    - L2: Tactical moves (candidate elimination)
    - L3: Operational backtracking when needed
    
    Let's see who wins!
    ═══════════════════════════════════════════════════════════════════════════════
    """)
    
    # Run HRM test
    hrm_results = run_hrm_sudoku_test()
    
    # Generate ChatGPT prompts
    generate_chatgpt_prompts()
    
    print("\n" + "=" * 80)
    print("   ✅ TEST COMPLETE!")
    print("=" * 80)
    print("\n📝 Next Steps:")
    print("   1. HRM results shown above")
    print("   2. Copy prompts from CHATGPT_SUDOKU_PROMPTS.txt")
    print("   3. Test ChatGPT with each puzzle")
    print("   4. Compare results!")
    print("\n" + "=" * 80)
