# Gomoku

## Board
For an $n\times n$ board we index the top left corner as $(0,0)$. A larger $x$ coordinate brings us more right relative to the origin. A larger $y$ coordinate brings us more down relative to the origin. This scheme is illustrated on the following $15\times15$ board.

<img src="/images/board.png" width=50% height=50%>


## Checking Win Conditions
We check whether a player has won after each placement, by counting the number of consecutive stones in each direction. The following function counts the number of consecutive stones specified by 
the parameters $dx$ and $dy$. For any such direction we must look further and back at most 4 stones, and we can break whenever we see a space which is occupied by another stone or is empty.
```python
def count_consecutive(self, x: int, y: int, dx: int, dy: int, player: Stone) -> int:
        """Counts the number of consecutive stones vertically, horizontally and diagonally"""
        count = 1
        opponent = Stone(player * -1)

        for i in range(1, 5):
            if self.in_bounds(x + i * dx, y + i * dy):
                if self.board[y + i * dy][x + i * dx] == player:
                    count += 1
                elif self.board[y + i * dy][x + i * dx] == opponent or self.board[y + i * dy][x + i * dx] == Stone.EMPTY:
                    break

        for i in range(1, 5):
            if self.in_bounds(x - i * dx, y - i * dy):
                if self.board[y - i * dy][x - i * dx] == player:
                    count += 1
                elif self.board[y - i * dy][x - i * dx] == opponent or self.board[y - i * dy][x - i * dx] == Stone.EMPTY:
                    break

        return count
```
## Static Evaluations
The following evaluation function which evaluates the state of the board at the instance the function is called
```python
def evaluate_board(self) -> int:
        """Gives a score of the current board"""
        with Timer('Evaluation'):
            if self.hash_for_board in self.transposition_table:
                return self.transposition_table[self.hash_for_board]
            
            white_score = (self.evaluate_horizontals(Stone.WHITE, self.min_y, self.max_y + 1) 
                        + self.evaluate_verticals(Stone.WHITE, self.min_x, self.max_x + 1) 
                        + self.evaluate_diagonals(Stone.WHITE))


            black_score = (self.evaluate_horizontals(Stone.BLACK, self.min_y, self.max_y + 1)
                        + self.evaluate_verticals(Stone.BLACK, self.min_x, self.max_x + 1)
                        + self.evaluate_diagonals(Stone.BLACK))
     
            self.transposition_table[self.hash_for_board] = white_score - black_score
        return self.transposition_table[self.hash_for_board]
```
### Evaluating horizontal and vertical lines
We track the number of stones in each horizontal and vertical linings of the board. When a stone is placed, we find the horizontal and vertical lining of the board for which that stone is placed and increment the associated variables by $1$.
```python
self.num_of_elements_in_rows: numpy.ndarray = numpy.zeros((self.board_size), dtype=int)
self.num_of_elements_in_cols: numpy.ndarray = numpy.zeros((self.board_size), dtype=int)
```
When making a static evaluation of the board we only score lines if they are occupied by at least one stone. In the following picture, for example, we would only evaluate the column at $x=8$ since it is the only column with greater than or equal to $2$ elements. We would not evaluate any rows
since no rows contain more than or equalt to $2$ elements. 

<img src="/images/Static_evluation.png" width=50% height=50%>

Furthermore, we record the minimum and maximum values of the $x$ and $y$ coordinates when placing stones on the board and only check for those columns and rows for values inside those constraints. These values are update for each placement
```python
def update_box(self, x: int, y: int):
        if x < self.min_x:
            self.min_x = x
        if x > self.max_x:
            self.max_x = x

        if y < self.min_y:
            self.min_y = y
        if y > self.max_y:
            self.max_y = y
```
This is such that when evaluating columns or rows we do not have to go through spaces where there is no stones. In the following example, $x_{\text{min}} = y_{\text{min}} = 5$ with $x_{\text{max}} = 10$ and $y_{\text{max}} = 12$ and so it suffices to score the horizontal and vertical lines within those values.

<img src="/images/bounding_box.png" width=50% height=50%>
In practice, to accomodate our evaluation function, which relies on window matching, we cannot put the tightest bound on the number of operations. We must add some buffer to our window such that the scoring function works properly

```python
def evaluate_verticals(self, player: Stone, lower: int, upper: int) -> int:
        """Evaluate the possible verticals"""
        lower_bound = numpy.max([0, lower])
        upper_bound = numpy.min([self.board_size-1, upper])

        input_lines = []

        if numpy.diff([self.max_y + 2, self.min_y -1]) < 6:
            buffer = self.max_pattern_len - 1
            start_y = max(0, self.min_y - buffer)
            end_y = min(self.board_size, self.max_y + buffer + 1)
        else:
            start_y = max(0, self.min_y - 1)
            end_y = min(self.board_size, self.max_y + 2)

        for x in range(lower_bound, upper_bound):
            if self.num_of_elements_in_cols[x] >= 2:
                col = [self.board[y][x] for y in range(start_y, end_y)]
                input_lines.append(col)

        return sum(self.score_line(input_lines, player))
```

### Evaluating diagonals
#### A characterization of diagonals
For convenience, suppose $d$ is a diagonal with end points $p_1 = (x_1, y_1)$ and $p_2 = (x_2, y_2)$ we call a diagonal a left diagonal if $x_1 < x_2$ and $y_1< y_2$ and a diagonal a right diagonal if $x_1 < x_2$ and $y_2< y_1$. This is best illustrated by the following diagram. The blue line is a left diagonal and the red line is a right diagonal.

<img src="/images/diagonals.png" width=56% height=56%>

#### Left diagonals
Since there are more than one diagonal where stones can be placed to form a five in a row, we employ the following labeling scheme for labeling the diagonals. We shall demonstrate this scheme on a $15\times15$ board for convenience, although
this scheme can be generalized to any $n\times n$ board. Consider some placement of some stone $s$ on a $15\times 15$ board at **$p=(x,y)$ and take the difference $x-y = k$**. We consider the stone $s$ as belonging to the $k+(board size-1)$ th left diagonal. For example,
suppose player one placed a white stone on **$(3,8)$, then that stone belongs to the $9$ th left diagonal**, illustrated by the blue line in the following diagram.

<img src="/images/scheme_left_diagonal.png" width=50% height=50%>

#### Right diagonals
Consider another of some stone $s$ on a $15\times 15$ board at **$p=(x,y)$ and take the sum $x+y = k$**. We consider the stone $s$ as belonging to the $k$ th left diagonal. For example,
suppose player one placed a white stone on **$(7,9)$, then that stone belongs to the $16$ th right diagonal**, illustrated by the red line in the following diagram.

<img src="/images/scheme_right_diagonal.png" width=50% height=50%>

#### In Practice
We track left diagonals and right diagonals during placement
```python
def place(self, x: int, y: int) -> bool:
    ...
    right_diagonal_index = x + y
    left_diagonal_index = x - y + self.board_size - 1
    
    self.num_of_elements_in_right_diagonals[right_diagonal_index] += 1
    self.num_of_elements_in_left_diagonals[left_diagonal_index] += 1
```
We use theses values recorded in our evaluating diagonals functions where we skip diagonals without more than $2$ stones. The code above has a fundamentally
similar logic as when evaluating verticals and horizontals. Namely, we go through the diagonals and score those diagonals with the score line function. 
```python
def evaluate_left_diagonals(self, player: Stone) -> int:
        """Evaluate the possible left diagonals"""
        score = 0
        mid_line = self.board_size - 1
        for index in range(4, len(self.num_of_elements_in_left_diagonals)-4): 
            if self.num_of_elements_in_left_diagonals[index] >= 2:
                if index <= mid_line: 
                    start_y = -index + self.board_size  - 1
                    line = [self.board[start_y + i][i] for i in range(index + 1)]
                    score += self.score_line(line, player)
                
                else: 
                    start_x = index - self.board_size + 1
                    line = [self.board[i][start_x + i] for i in range(2 * mid_line + 1- index)]
                    score += self.score_line(line, player)   

        return score
```
The difficulty lies in the fact of determining the number of elements in a diagonal and determining the index to start gathering those elements. To 
solve this problem we introduce what is named in the function as the mid line. In a $15\times 15$ board a midline is the left diagonal which is the $14$ th diagonal. We consider
diagonals with index less than or equal to $14$ differently than diagonals with index more than $14$. In particular, notice that the length of the elements in any $k$ th diagonal where
$k<=14$ is $k+1$, which is the reason for
```python
line = [self.board[start_y + i][i] for i in range(index + 1)]
```
In a similar manner, the starting $x$ and $y$ are computed differently depending on the position of the line. This is arguably arbitrary, but we chose to gather from the left to the right, which means that
left diagonals to the right of the mid line all start from $y=0$ with some $x$ coordinate that is a function of the index and board size.

There exists a way to bound the number of operations by the minimum and maximum $x,y$ values just like the horizontal evaluations and vertical evaluations, however the implementation requires a non trivial amount of
tricks involving the indexing of the elements of the board and may only bring us a somewhat minor gain in performance, so I have not implemented it for the diagonal evaluations.

### Scoring function
The scoring function creates a sliding window on the lines passed in and tries to match the window with pre determined patterns. If it exists, then 
we increment the score by the weight given to the pattern.
```python
def score_line(self, lines: list[list[Stone]], player: Stone) -> list[int]:
        pattern_score = self.pattern_score if player == Stone.WHITE else self.inverted_pattern_score
        max_len = max(len(pat) for pat in self.pattern_score)
        outputs = []
        for line in lines:
            score = 0
            for window_size in range(3, max_len + 1):
                for i in range(len(line) - window_size + 1):
                    window = tuple(line[i:i + window_size])
                    if window in pattern_score:
                        val = pattern_score[window]
                        score += val
            outputs.append(score)
        return outputs
```




















