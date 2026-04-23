
import java.util.Scanner;

public class Main {

    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        char[][] ans = new char[8][8];
        for (int i = 0; i < 8; i++) {
            String str = sc.next();
            for (int j = 0; j < 8; j++) {
                ans[i][j] = str.charAt(j);
            }
        }
        if (dfs(0, ans)) {
            for (int i = 0; i < 8; i++) {
                for (int j = 0; j < 8; j++) {
                    System.out.print(ans[i][j]);
                }
                System.out.println();
            }
        } else {
            System.out.println("No Answer");
        }
    }

    static boolean isPuttable(int y, int x, char[][] ans) {
        for (int i = -1; i <= 1; i++) {
            for (int j = -1; j <= 1; j++) {
                if (i == 0 && j == 0) continue;
                int total1 = y;
                int total2 = x;
                while (true) {
                    total1 += i;
                    total2 += j;
                    if (total1 < 0 || total2 < 0 || total1 >= 8 || total2 >= 8) break;
                    if (ans[total1][total2] == 'Q') return false;
                }
            }
        }
        return true;
    }


    static boolean dfs(int y, char[][] ans) {
        if (y == 8) return true;
        int cnt = -1;

        for (int i = 0; i < 8; i++) {
            if (ans[y][i] == 'Q') {
                if (cnt == -1) cnt = i;
                else return false;
            }
        }

        if (cnt != -1) {
            if (isPuttable(y, cnt, ans) && dfs(y + 1, ans)) {
                return true;
            }
        }
        else {
            for (int i = 0; i < 8; i++) {
                if (isPuttable(y, i, ans)) {
                    ans[y][i] = 'Q';
                    if (dfs(y + 1, ans)) return true;
                    else ans[y][i] = '.';
                }
            }
        }
        return false;
    }


}