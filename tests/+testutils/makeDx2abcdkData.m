function data = makeDx2abcdkData(kind, varargin)
%makeDx2abcdkData  Deterministic datasets for dx2abcdk testing/parity.
%
% data fields:
%   x   - n-by-(N-p) state sequence (as expected by dx2abcdk)
%   u   - N-by-r input sequence
%   y   - N-by-l output sequence
%   f,p - window sizes
%   A0,B0,C0,D0,K0 - ground-truth simulation matrices

if nargin < 1 || isempty(kind)
    kind = 'stable';
end

p = inputParser;
p.addParameter('N', 240);
p.addParameter('seed', 21);
p.addParameter('f', 5);
p.addParameter('p', 10);
p.parse(varargin{:});
opt = p.Results;

rng(opt.seed, 'twister');

n = 2;
r = 1;
l = 1;

if strcmpi(kind, 'unstable')
    A0 = [1.12 0.03; 0.00 1.03];
else
    A0 = [0.72 0.10; -0.08 0.64];
end
B0 = 0.2 * randn(n, r);
C0 = 0.4 * randn(l, n);
D0 = 0.05 * randn(l, r);
K0 = 0.08 * randn(n, l);

N = opt.N;
u = randn(r, N);
e = 0.02 * randn(l, N);
xfull = zeros(n, N);
y = zeros(l, N);

for k = 1:(N-1)
    y(:,k) = C0*xfull(:,k) + D0*u(:,k) + e(:,k);
    xfull(:,k+1) = A0*xfull(:,k) + B0*u(:,k) + K0*e(:,k);
end
y(:,N) = C0*xfull(:,N) + D0*u(:,N) + e(:,N);

% Match dmodx-style state sequence used by dx2abcdk.
x = xfull(:, opt.p+1:N);

% Return u/y as N-by-1 column vectors, as commonly used in toolbox tests.
data = struct();
data.x = x;
data.u = u';
data.y = y';
data.f = opt.f;
data.p = opt.p;
data.A0 = A0;
data.B0 = B0;
data.C0 = C0;
data.D0 = D0;
data.K0 = K0;
end
