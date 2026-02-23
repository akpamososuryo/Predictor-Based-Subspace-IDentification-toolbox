function [u, y, meta] = makeNonlinearData(varargin)
%makeNonlinearData  Deterministic datasets for nonlinear model tests.
%
% Supported types:
%   'hammerstein'         input nonlinearity then linear dynamics
%   'wiener'              linear dynamics then output nonlinearity
%   'hammersteinwiener'   both
%
% Name-value parameters:
%   'type'      (default 'hammerstein')
%   'N'         (default 220)
%   'seed'      (default 60)
%   'noiseStd'  (default 0.03)

p = inputParser;
p.addParameter('type', 'hammerstein');
p.addParameter('N', 220);
p.addParameter('seed', 60);
p.addParameter('noiseStd', 0.03);
p.parse(varargin{:});
opt = p.Results;

rng(opt.seed, 'twister');

N = opt.N;
u = randn(N,1);

% Static nonlinearities
fin  = @(x) x + 0.2*x.^3;       % input nonlinearity
fout = @(x) x + 0.1*x.^3;       % output nonlinearity

% Linear dynamics (stable first-order)
a = 0.7;
b = 0.2;

z = zeros(N,1);   % internal linear state/output before output nonlinearity
y = zeros(N,1);

e = opt.noiseStd * randn(N,1);

switch lower(opt.type)
    case 'hammerstein'
        ueff = fin(u);
        for k = 2:N
            y(k) = a*y(k-1) + b*ueff(k-1) + e(k);
        end

    case 'wiener'
        for k = 2:N
            z(k) = a*z(k-1) + b*u(k-1);
        end
        y = fout(z) + e;

    case 'hammersteinwiener'
        ueff = fin(u);
        for k = 2:N
            z(k) = a*z(k-1) + b*ueff(k-1);
        end
        y = fout(z) + e;

    otherwise
        error('Unknown type: %s', opt.type);
end

meta = struct();
meta.type = opt.type;
meta.N = N;
meta.seed = opt.seed;
meta.noiseStd = opt.noiseStd;
meta.a = a;
meta.b = b;
end