import java.io.BufferedWriter;
import java.io.FileInputStream;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.util.Arrays;
import java.util.HashMap;
import java.util.PriorityQueue;
import java.util.Queue;

public class Main {
	public static void main(String[] args) throws NumberFormatException,
	IOException {Main solve = new Main();solve.solve();}
	void dump(int[]a){for(int i=0;i<a.length;i++)System.out.print(a[i]+" ");System.out.println();}
	void dump(int[]a,int n){for(int i=0;i<a.length;i++)System.out.printf("%"+n+"d",a[i]);System.out.println();}
	void dump(long[]a){for(int i=0;i<a.length;i++)System.out.print(a[i]+" ");System.out.println();}
	void dump(char[]a){for(int i=0;i<a.length;i++)System.out.print(a[i]);System.out.println();}
	long pow(long a,int n){long r=1;while(n>0){if((n&1)==1)r*=a;a*=a;n>>=1;}return r;}
	String itob(int a,int l){return String.format("%"+l+"s",Integer.toBinaryString(a)).replace(' ','0');}
	void sort(int[]a){m_sort(a,0,a.length,new int[a.length]);}
	void m_sort(int[]a, int s, int sz, int[]b){
		if(sz<7){for(int i=s;i<s+sz;i++)for(int j=i;j>s&&a[j-1]>a[j];j--)swap(a, j, j-1);return;}
		m_sort(a,s,sz/2,b);m_sort(a,s+sz/2,sz-sz/2,b);int idx=s;int l=s,r=s+sz/2;final int le=s+sz/2,re=s+sz;
		while(l<le&&r<re){if(a[l]>a[r])b[idx++]=a[r++];else b[idx++]=a[l++];}
		while(r<re)b[idx++]=a[r++];while(l<le)b[idx++]=a[l++];for(int i=s;i<s+sz;i++)a[i]=b[i];
	} /* qsort(3.5s)<<msort(9.5s)<<<shuffle+qsort(17s)<Arrays.sort(Integer)(20s) */
	void swap(int[] a,int i,int j){final int t=a[i];a[i]=a[j];a[j]=t;}
	int binarySearchSmallerMax(int[]a,int v)// get maximum index which a[idx]<=v
	{int l=0,r=a.length-1,s=0;while(l<=r){int m=(l+r)/2;if(a[m]>v)r=m-1;else{l=m+1;s=m;}}return a[s]>v?-1:s;}
	void solve() throws NumberFormatException, IOException{
		ContestScanner in = new ContestScanner();
		Writer out = new Writer();
		int h = in.nextInt();
		int w = in.nextInt();
		int[][] dp = new int[h][w];
		int[][] map = new int[h][w];
//		Pos[] pos = new Pos[h*w];
		long[] pos = new long[h*w];
		for(int i=0; i<h; i++){
			for(int j=0; j<w; j++){
				map[i][j] = in.nextInt();
				pos[i*w+j] = (long)map[i][j]<<32|i<<11|j;
//				pos[i*w+j] = new Pos(i*w+j, map[i][j]);
			}
		}
		Arrays.sort(pos);
		final int[] dy = {1, 0, -1, 0};
		final int[] dx = {0, 1, 0, -1};
		final int mod = 1000000007;
		int sum = 0;
		long mask = (1L<<32)-1;
		int maskS = (1<<11)-1;
		for(int t=0; t<pos.length; t++){
			long p = pos[t];
			final int y = (int)((p&mask)>>11);
			final int x = (int)((p&mask)&maskS);
			dp[y][x]++;
			if(dp[y][x]>=mod) dp[y][x] -= mod;
			for(int i=0; i<4; i++){
				final int ny = y+dy[i];
				final int nx = x+dx[i];
				if(ny<0||ny>=h||nx<0||nx>=w||map[ny][nx]<=map[y][x]) continue;
				dp[ny][nx] += dp[y][x];
				if(dp[ny][nx]>=mod) dp[ny][nx] -= mod;
			}
			sum += dp[y][x];
			if(sum>=mod) sum -= mod;
		}
		System.out.println(sum);
	}
}
//
//class Pos implements Comparable<Pos>{
//	int p, v;
//	Pos(int p, int v){
//		this.p = p;
//		this.v = v;
//	}
//	@Override
//	public int compareTo(Pos o) {
//		return v-o.v;
//	}
//}
class MultiSet<T> extends HashMap<T, Integer>{
	@Override
	public Integer get(Object key){return containsKey(key)?super.get(key):0;}
	public void add(T key,int v){put(key,get(key)+v);}
	public void add(T key){put(key,get(key)+1);}
	public void sub(T key)
	{final int v=get(key);if(v==1)remove(key);else put(key,v-1);}
}
class Timer{
	long time;
	public void set(){time=System.currentTimeMillis();}
	public long stop(){return time=System.currentTimeMillis()-time;}
	public void print()
	{System.out.println("Time: "+(System.currentTimeMillis()-time)+"ms");}
	@Override public String toString(){return"Time: "+time+"ms";}
}
class Writer extends PrintWriter{
	public Writer(String filename)throws IOException
	{super(new BufferedWriter(new FileWriter(filename)));}
	public Writer()throws IOException{super(System.out);}
}
class ContestScanner {
	private InputStreamReader in;private int c=-2;
	public ContestScanner()throws IOException 
	{in=new InputStreamReader(System.in);}
	public ContestScanner(String filename)throws IOException
	{in=new InputStreamReader(new FileInputStream(filename));}
	public String nextToken()throws IOException {
		StringBuilder sb=new StringBuilder();
		while((c=in.read())!=-1&&Character.isWhitespace(c));
		while(c!=-1&&!Character.isWhitespace(c)){sb.append((char)c);c=in.read();}
		return sb.toString();
	}
	public String readLine()throws IOException{
		StringBuilder sb=new StringBuilder();if(c==-2)c=in.read();
		while(c!=-1&&c!='\n'&&c!='\r'){sb.append((char)c);c=in.read();}
		return sb.toString();
	}
	public long nextLong()throws IOException,NumberFormatException
	{long r=0;while((c=in.read())!=-1&&Character.isWhitespace(c));
	while(c!=-1&&!Character.isWhitespace(c)){r*=10;r+=c-'0';c=in.read();}return r;}
	public int nextInt()throws NumberFormatException,IOException
	{return(int)nextLong();}
	public double nextDouble()throws NumberFormatException,IOException 
	{return Double.parseDouble(nextToken());}
}