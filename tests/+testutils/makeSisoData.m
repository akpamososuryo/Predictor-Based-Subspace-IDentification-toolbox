function [u, y, sys] = makeSisoData(varargin)
%makeSisoData  Deterministic SISO dataset generator for unit tests.
%
% Generates data from a stable discrete-time state-space model:
%   x(k+1) = A*x(k) + B*u(k) + w(k)
%   y(k)   = C*x(k) + D*u(k) + v(k)
%
% Returns u and y as N-by-1 column vectors.
%
% Name-value parameters:
%   'N'               Number of samples (default 400)
%   'seed'            RNG seed (default 0)
%   'A','B','C','D'   System scalars (defaults A=0.7, B=0.2, C=1, D=0)
%   'x0'              Initial state (default 0)
%   'noiseStd'        Measurement noise std dev (default 0.02)
%   'processNoiseStd' Process noise std dev (default 0)

p = inputParser;
p.addParameter('N', 400);
p.addParameter('seed', 0);
p.addParameter('A', 0.7);
p.addParameter('B', 0.2);
p.addParameter('C', 1.0);
p.addParameter('D', 0.0);
p.addParameter('x0', 0.0);
p.addParameter('noiseStd', 0.02);
p.addParameter('processNoiseStd', 0.0);
p.parse(varargin{:});
opt = p.Results;

rng(opt.seed, 'twister')

N = opt.N;
A = opt.A; B = opt.B; C = opt.C; D = opt.D;

u = randn(N,1);

x = zeros(N, 1);
x(1) = opt.x0;

w = opt.processNoiseStd * randn(N, 1);
v = opt.noiseStd * randn(N, 1);

for k = 1:(N-1);
    x(k+1) = A * x(k) + B * u(k) + w(k);
end

yClean = C * x + D * u;
y = yClean + v;

sys = struct();
sys.N = N;
sys.seed = opt.seed;
sys.A = A; sys.B = B; sys.C = C; sys.D = D;
sys.x = x;
sys.yClean = yClean;
sys.noiseStd = opt.noiseStd;
sys.processNoiseStd = opt.processNoiseStd;

end