function [u, y, mu, meta] = makeLpvData(varargin)
%makeLpvData  Deterministic SISO LPV dataset generator for unit tests.
%
% Produces a 1-state affine LPV system with one scheduling parameter rho:
%   x(k+1) = (A0 + A1*rho(k)) x(k) + (B0 + B1*rho(k)) u(k) + w(k)
%   y(k)   = C x(k) + D u(k) + v(k)
%
% Output:
%   u   N-by-1
%   y   N-by-1
%   mu  N-by-2, mu(:,1)=1 and mu(:,2)=rho
%   meta struct with true parameters and generated signals

p = inputParser;
p.addParameter('N', 600);
p.addParameter('seed', 30);
p.addParameter('noiseStd', 0.03);
p.addParameter('processNoiseStd', 0.0);
p.addParameter('rhoType', 'random');   % 'random' or 'periodic'
p.addParameter('period', 20);          % used when rhoType='periodic'

% True system parameters (stable across rho range used below)
p.addParameter('A0', 0.60);
p.addParameter('A1', 0.10);
p.addParameter('B0', 0.30);
p.addParameter('B1', 0.05);
p.addParameter('C',  1.00);
p.addParameter('D',  0.00);

p.parse(varargin{:});
opt = p.Results;

rng(opt.seed, 'twister');

N = opt.N;
u = randn(N,1);

% Scheduling signal rho
switch lower(opt.rhoType)
    case 'random'
        % Bounded random scheduling in roughly [-0.6, 0.6]
        rho = 0.6 * tanh(randn(N,1));
    case 'periodic'
        k = (0:N-1)';
        rho = 0.5 * cos(2*pi*k/opt.period) + 0.2; % roughly [-0.3, 0.7]
    otherwise
        error('Unknown rhoType: %s', opt.rhoType);
end

% Build mu with constant term first
mu = [ones(N,1) rho];

% Simulate
x = zeros(N,1);
w = opt.processNoiseStd * randn(N,1);
v = opt.noiseStd * randn(N,1);

for k = 1:(N-1)
    Aeff = opt.A0 + opt.A1 * rho(k);
    Beff = opt.B0 + opt.B1 * rho(k);
    x(k+1) = Aeff * x(k) + Beff * u(k) + w(k);
end

yClean = opt.C * x + opt.D * u;
y = yClean + v;

meta = struct();
meta.N = N;
meta.seed = opt.seed;
meta.u = u;
meta.rho = rho;
meta.mu = mu;
meta.x = x;
meta.yClean = yClean;
meta.A0 = opt.A0; meta.A1 = opt.A1;
meta.B0 = opt.B0; meta.B1 = opt.B1;
meta.C = opt.C; meta.D = opt.D;
meta.noiseStd = opt.noiseStd;
meta.processNoiseStd = opt.processNoiseStd;
end