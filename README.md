# Gomoku


## Board
For an $n\times n$ board we index the top left corner as $(0,0)$. A larger $x$ coordinate brings us more right relative to the origin. A larger $y$ coordinate brings us more down relative to the origin. This scheme is illustrated on the following $15\times15$ board.

<img src="/images/board.png" width=50% height=50%>

## Heuristics
We call a line a diagonal if it has two endpoints $p_1=(x_1,y_1)$ and $p_2 =(x_2,y_2)$ with $x_1 < x_2$ and $y_1< y_2$ or $y_2<y_1$. For convenience, we call a diagonal a left diagonal if $x_1 < x_2$ and $y_1< y_2$ and 
right if $x_1 < x_2$ and $y_2< y_1$. This is best illustrated by the following diagram, where the blue line a left diagonal and the red line a right diagonal.

<img src="/images/diagonals.png" width=56% height=56%>
