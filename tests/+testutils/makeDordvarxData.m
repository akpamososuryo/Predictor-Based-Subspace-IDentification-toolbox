function data = makeDordvarxData(varargin)
%makeDordvarxData  Deterministic input/output data for dordvarx parity tests.
%
% data fields:
%   u, y - N-by-r and N-by-l identification data
%   f, p - window sizes

p = inputParser;
p.addParameter('N', 260);
p.addParameter('seed', 71);
p.addParameter('f', 5);
p.addParameter('p', 10);
p.addParameter('r', 2);
p.addParameter('l', 1);
p.parse(varargin{:});
opt = p.Results;

rng(opt.seed, 'twister');

N = opt.N;
r = opt.r;
l = opt.l;

u = randn(r, N);

A0 = 0.85 * eye(l);
B0 = 0.30 * randn(l, r);
y = zeros(l, N);
for k = 2:N
    y(:,k) = A0 * y(:,k-1) + B0 * u(:,k-1);
end

data = struct();
data.u = u';
data.y = y';
data.f = opt.f;
data.p = opt.p;
end
