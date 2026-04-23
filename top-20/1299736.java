import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.util.Arrays;
import java.util.Objects;
import java.util.StringTokenizer;

public class Main {

	public static void main(String args[]) {
		FastScanner cin = new FastScanner();
		PrintWriter cout = new PrintWriter(System.out);
		solve(cin, cout);
		cout.flush();
	}

	private static void solve(FastScanner cin, PrintWriter cout) {
		// 自前の例
		assert Objects.equals(
				solve(4, 5, new int[][] { { 1, 4, 1 }, { 2, 3, 1 }, { 3, 2, 1 }, { 3, 4, 1 }, { 1, 2, 1 } }), "inf");
		// 問題の例
		assert Objects.equals(solve(3, 3, new int[][] { { 1, 2, 4 }, { 2, 3, 3 }, { 1, 3, 5 } }), "7");
		assert Objects.equals(solve(2, 2, new int[][] { { 1, 2, 1 }, { 2, 1, 1 } }), "inf");
		assert Objects.equals(solve(6, 5, new int[][] { { 1, 2, -1000000000 }, { 2, 3, -1000000000 },
				{ 3, 4, -1000000000 }, { 4, 5, -1000000000 }, { 5, 6, -1000000000 } }), "-5000000000");

		int n = cin.nextInt();
		int m = cin.nextInt();
		int[][] abcs = new int[m][];
		for (int i = 0; i < abcs.length; i++)
			abcs[i] = new int[] { cin.nextInt(), cin.nextInt(), cin.nextInt() };

		String ans = solve(n, m, abcs);
		cout.println(ans);
	}

	private static String solve(int n, int m, int[][] abcs) {
		// https://en.wikipedia.org/wiki/Bellman%E2%80%93Ford_algorithm
		long[] dist = new long[n + 1];
		Arrays.fill(dist, Long.MAX_VALUE / 2);
		dist[1] = 0;
		int[][] edges = new int[abcs.length][];
		for (int i = 0; i < abcs.length; i++)
			edges[i] = new int[] { abcs[i][0], abcs[i][1], -abcs[i][2] };
		for (int i = 2; i < dist.length; i++)
			for (int[] e : edges)
				dist[e[1]] = Math.min(dist[e[1]], dist[e[0]] + e[2]);
		long ans = dist[n];
		// negative-weight cycleの扱いがwikiと違う理由
		// wikiの場合、グラフの中のどこかに含まれるとアウト
		// この問題の場合、1-nの経路の中に含まれるとアウト
		for (int i = 2; i < dist.length; i++)
			for (int[] e : edges)
				dist[e[1]] = Math.min(dist[e[1]], dist[e[0]] + e[2]);
		if (ans != dist[n])
			return "inf";

		return Long.toString(-ans);
	}

	/**
	 * How to read input in Java — tutorial <br />
	 * By Flatfoot<br />
	 * http://codeforces.com/blog/entry/7018
	 */
	static class FastScanner {
		private BufferedReader br;
		private StringTokenizer st;

		FastScanner() {
			br = new BufferedReader(new InputStreamReader(System.in));
		}

		String next() {
			while (st == null || !st.hasMoreElements())
				try {
					st = new StringTokenizer(br.readLine());
				} catch (IOException e) {
					throw new IllegalStateException(e);
				}
			return st.nextToken();
		}

		double nextDouble() {
			return Double.parseDouble(next());
		}

		int nextInt() {
			return Integer.parseInt(next());
		}

		String nextLine() {
			String str = "";
			try {
				str = br.readLine();
			} catch (IOException e) {
				throw new IllegalStateException(e);
			}
			return str;
		}

		long nextLong() {
			return Long.parseLong(next());
		}
	}

}
