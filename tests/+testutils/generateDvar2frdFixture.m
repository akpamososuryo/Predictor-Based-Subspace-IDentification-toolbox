function generateDvar2frdFixture(outputPath)
%generateDvar2frdFixture  Write MATLAB reference fixture for dvar2frd parity tests.
%
% Usage:
%   testutils.generateDvar2frdFixture
%   testutils.generateDvar2frdFixture('fixtures/matlab_reference/dvar2frd_fixture.mat')

if nargin < 1 || isempty(outputPath)
    repoRoot = fileparts(fileparts(fileparts(mfilename('fullpath'))));
    outputPath = fullfile(repoRoot, 'fixtures', 'matlab_reference', 'dvar2frd_fixture.mat');
end

outDir = fileparts(outputPath);
if ~exist(outDir, 'dir')
    mkdir(outDir);
end

p = 4;
l = 2;
r = 1;
h = 0.05;
w = linspace(0.2, 2.0, 6);
nw = length(w);
n_cases = 3;

% VARX mode fixtures (3 cases)
m = l + r;
nParam = p * l * (l + r) + r * l;
VARX_cases = zeros(l, p * m + r, n_cases);
P_varx_cases = zeros(nParam, nParam, n_cases);
w_varx_cases = zeros(nw, n_cases);
h_varx_cases = zeros(1, n_cases);
p_varx_cases = zeros(1, n_cases);
G_varx_cases = complex(zeros(l, r + l, nw, n_cases));
covG_varx_cases = zeros(l, r + l, nw, 2, 2, n_cases);

for i = 1:n_cases
    rng(90 + i);
    VARX_cases(:, :, i) = 0.2 .* randn(l, p * m + r);
    P_varx_cases(:, :, i) = (1e-3 * (1 + 0.1 * (i - 1))) .* eye(nParam);
    w_varx_cases(:, i) = w(:);
    h_varx_cases(i) = h;
    p_varx_cases(i) = p;
    [G_i, covG_i] = dvar2frd(P_varx_cases(:, :, i), w, h, p, VARX_cases(:, :, i));
    G_varx_cases(:, :, :, i) = G_i;
    covG_varx_cases(:, :, :, :, :, i) = covG_i;
end

% ABCK/ABCDK mode fixtures (3 cases)
n = 3;
r2 = 2;
l2 = 2;
nParamABCK = n^2 + (r2 + l2) * n + n * l2;
nParamABCDK = nParamABCK + r2 * l2;

A_abck_cases = zeros(n, n, n_cases);
B_abck_cases = zeros(n, r2, n_cases);
C_abck_cases = zeros(l2, n, n_cases);
K_abck_cases = zeros(n, l2, n_cases);
P_abck_cases = zeros(nParamABCK, nParamABCK, n_cases);
w_abck_cases = zeros(nw, n_cases);
h_abck_cases = zeros(1, n_cases);
G_abck_cases = complex(zeros(l2, r2 + l2, nw, n_cases));
covG_abck_cases = zeros(l2, r2 + l2, nw, 2, 2, n_cases);

A_abcdk_cases = zeros(n, n, n_cases);
B_abcdk_cases = zeros(n, r2, n_cases);
C_abcdk_cases = zeros(l2, n, n_cases);
D_abcdk_cases = zeros(l2, r2, n_cases);
K_abcdk_cases = zeros(n, l2, n_cases);
P_abcdk_cases = zeros(nParamABCDK, nParamABCDK, n_cases);
w_abcdk_cases = zeros(nw, n_cases);
h_abcdk_cases = zeros(1, n_cases);
G_abcdk_cases = complex(zeros(l2, r2 + l2, nw, n_cases));
covG_abcdk_cases = zeros(l2, r2 + l2, nw, 2, 2, n_cases);

for i = 1:n_cases
    rng(110 + i);
    A_i = [0.83 0.08 0.00; -0.05 0.79 0.04; 0.00 0.03 0.74] + 0.01 * (i - 1) * eye(n);
    B_i = 0.2 .* randn(n, r2);
    C_i = 0.2 .* randn(l2, n);
    K_i = 0.1 .* randn(n, l2);
    D_i = 0.05 .* randn(l2, r2);

    A_abck_cases(:, :, i) = A_i;
    B_abck_cases(:, :, i) = B_i;
    C_abck_cases(:, :, i) = C_i;
    K_abck_cases(:, :, i) = K_i;
    P_abck_cases(:, :, i) = (1e-3 * (1 + 0.1 * (i - 1))) .* eye(nParamABCK);
    w_abck_cases(:, i) = w(:);
    h_abck_cases(i) = h;
    [G_abck_i, covG_abck_i] = dvar2frd(P_abck_cases(:, :, i), w, h, A_i, B_i, C_i, K_i);
    G_abck_cases(:, :, :, i) = G_abck_i;
    covG_abck_cases(:, :, :, :, :, i) = covG_abck_i;

    A_abcdk_cases(:, :, i) = A_i;
    B_abcdk_cases(:, :, i) = B_i;
    C_abcdk_cases(:, :, i) = C_i;
    D_abcdk_cases(:, :, i) = D_i;
    K_abcdk_cases(:, :, i) = K_i;
    P_abcdk_cases(:, :, i) = (1e-3 * (1 + 0.1 * (i - 1))) .* eye(nParamABCDK);
    w_abcdk_cases(:, i) = w(:);
    h_abcdk_cases(i) = h;
    [G_abcdk_i, covG_abcdk_i] = dvar2frd(P_abcdk_cases(:, :, i), w, h, A_i, B_i, C_i, D_i, K_i);
    G_abcdk_cases(:, :, :, i) = G_abcdk_i;
    covG_abcdk_cases(:, :, :, :, :, i) = covG_abcdk_i;
end

% Backward-compatible single-case aliases (case 1).
P = P_varx_cases(:, :, 1); %#ok<NASGU>
VARX = VARX_cases(:, :, 1); %#ok<NASGU>
G = G_varx_cases(:, :, :, 1); %#ok<NASGU>
covG = covG_varx_cases(:, :, :, :, :, 1); %#ok<NASGU>

A = A_abck_cases(:, :, 1); %#ok<NASGU>
B = B_abck_cases(:, :, 1); %#ok<NASGU>
C = C_abck_cases(:, :, 1); %#ok<NASGU>
K = K_abck_cases(:, :, 1); %#ok<NASGU>
P_abck = P_abck_cases(:, :, 1); %#ok<NASGU>
G_abck = G_abck_cases(:, :, :, 1); %#ok<NASGU>
covG_abck = covG_abck_cases(:, :, :, :, :, 1); %#ok<NASGU>

D = D_abcdk_cases(:, :, 1); %#ok<NASGU>
P_abcdk = P_abcdk_cases(:, :, 1); %#ok<NASGU>
G_abcdk = G_abcdk_cases(:, :, :, 1); %#ok<NASGU>
covG_abcdk = covG_abcdk_cases(:, :, :, :, :, 1); %#ok<NASGU>

meta = struct();
meta.note = 'Deterministic MATLAB fixture for dvar2frd VARX/ABCK/ABCDK parity checks (3 cases each)';
meta.createdBy = 'testutils.generateDvar2frdFixture';
meta.n_cases = n_cases;

save(outputPath, ...
    'meta', ...
    'n_cases', ...
    'P_varx_cases', 'w_varx_cases', 'h_varx_cases', 'p_varx_cases', ...
    'VARX_cases', 'G_varx_cases', 'covG_varx_cases', ...
    'A_abck_cases', 'B_abck_cases', 'C_abck_cases', 'K_abck_cases', ...
    'P_abck_cases', 'w_abck_cases', 'h_abck_cases', 'G_abck_cases', 'covG_abck_cases', ...
    'A_abcdk_cases', 'B_abcdk_cases', 'C_abcdk_cases', 'D_abcdk_cases', 'K_abcdk_cases', ...
    'P_abcdk_cases', 'w_abcdk_cases', 'h_abcdk_cases', 'G_abcdk_cases', 'covG_abcdk_cases', ...
    'P', 'w', 'h', 'p', 'VARX', 'G', 'covG', ...
    'A', 'B', 'C', 'K', 'P_abck', 'G_abck', 'covG_abck', ...
    'D', 'P_abcdk', 'G_abcdk', 'covG_abcdk');

fprintf('Wrote fixture: %s\n', outputPath);
end
