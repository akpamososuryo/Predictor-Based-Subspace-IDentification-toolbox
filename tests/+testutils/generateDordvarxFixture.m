function generateDordvarxFixture(outputPath)
%generateDordvarxFixture  Write MATLAB reference fixture for Python parity tests.
%
% Usage:
%   testutils.generateDordvarxFixture
%   testutils.generateDordvarxFixture('fixtures/matlab_reference/dordvarx_fixture.mat')

if nargin < 1 || isempty(outputPath)
    repoRoot = fileparts(fileparts(fileparts(mfilename('fullpath'))));
    outputPath = fullfile(repoRoot, 'fixtures', 'matlab_reference', 'dordvarx_fixture.mat');
end

outDir = fileparts(outputPath);
if ~exist(outDir, 'dir')
    mkdir(outDir);
end

n_cases = 3;
seeds = [72 106 140];

for i = 1:n_cases
    d = testutils.makeDordvarxData('seed', seeds(i));

    [S_base_i, X_base_i, VARX_base_i, U_base_i, Zps_base_i] = dordvarx( ...
        d.u, d.y, d.f, d.p, 'none', 'gcv', 0, 0);
    [S_weight1_i, X_weight1_i, VARX_weight1_i, U_weight1_i, Zps_weight1_i] = dordvarx( ...
        d.u, d.y, d.f, d.p, 'none', 'gcv', 1, 0);
    [S_noD_i, X_noD_i, VARX_noD_i, U_noD_i, Zps_noD_i] = dordvarx( ...
        d.u, d.y, d.f, d.p, 'none', 'gcv', 0, 1);

    if i == 1
        u_c1 = d.u;
        y_c1 = d.y;
        f_c1 = d.f;
        p_c1 = d.p;
        S_base_c1 = S_base_i;
        X_base_c1 = X_base_i;
        VARX_base_c1 = VARX_base_i;
        U_base_c1 = U_base_i;
        Zps_base_c1 = Zps_base_i;
        S_weight1_c1 = S_weight1_i;
        X_weight1_c1 = X_weight1_i;
        VARX_weight1_c1 = VARX_weight1_i;
        U_weight1_c1 = U_weight1_i;
        Zps_weight1_c1 = Zps_weight1_i;
        S_noD_c1 = S_noD_i;
        X_noD_c1 = X_noD_i;
        VARX_noD_c1 = VARX_noD_i;
        U_noD_c1 = U_noD_i;
        Zps_noD_c1 = Zps_noD_i;
    elseif i == 2
        u_c2 = d.u;
        y_c2 = d.y;
        f_c2 = d.f;
        p_c2 = d.p;
        S_base_c2 = S_base_i;
        X_base_c2 = X_base_i;
        VARX_base_c2 = VARX_base_i;
        U_base_c2 = U_base_i;
        Zps_base_c2 = Zps_base_i;
        S_weight1_c2 = S_weight1_i;
        X_weight1_c2 = X_weight1_i;
        VARX_weight1_c2 = VARX_weight1_i;
        U_weight1_c2 = U_weight1_i;
        Zps_weight1_c2 = Zps_weight1_i;
        S_noD_c2 = S_noD_i;
        X_noD_c2 = X_noD_i;
        VARX_noD_c2 = VARX_noD_i;
        U_noD_c2 = U_noD_i;
        Zps_noD_c2 = Zps_noD_i;
    else
        u_c3 = d.u;
        y_c3 = d.y;
        f_c3 = d.f;
        p_c3 = d.p;
        S_base_c3 = S_base_i;
        X_base_c3 = X_base_i;
        VARX_base_c3 = VARX_base_i;
        U_base_c3 = U_base_i;
        Zps_base_c3 = Zps_base_i;
        S_weight1_c3 = S_weight1_i;
        X_weight1_c3 = X_weight1_i;
        VARX_weight1_c3 = VARX_weight1_i;
        U_weight1_c3 = U_weight1_i;
        Zps_weight1_c3 = Zps_weight1_i;
        S_noD_c3 = S_noD_i;
        X_noD_c3 = X_noD_i;
        VARX_noD_c3 = VARX_noD_i;
        U_noD_c3 = U_noD_i;
        Zps_noD_c3 = Zps_noD_i;
    end
end

% Backward-compatible single-case aliases (c1).
u_base = u_c1; %#ok<NASGU>
y_base = y_c1; %#ok<NASGU>
f_base = f_c1; %#ok<NASGU>
p_base = p_c1; %#ok<NASGU>
S_base = S_base_c1; %#ok<NASGU>
X_base = X_base_c1; %#ok<NASGU>
VARX_base = VARX_base_c1; %#ok<NASGU>
U_base = U_base_c1; %#ok<NASGU>
Zps_base = Zps_base_c1; %#ok<NASGU>
S_weight1 = S_weight1_c1; %#ok<NASGU>
X_weight1 = X_weight1_c1; %#ok<NASGU>
VARX_weight1 = VARX_weight1_c1; %#ok<NASGU>
U_weight1 = U_weight1_c1; %#ok<NASGU>
Zps_weight1 = Zps_weight1_c1; %#ok<NASGU>
S_noD = S_noD_c1; %#ok<NASGU>
X_noD = X_noD_c1; %#ok<NASGU>
VARX_noD = VARX_noD_c1; %#ok<NASGU>
U_noD = U_noD_c1; %#ok<NASGU>
Zps_noD = Zps_noD_c1; %#ok<NASGU>

meta = struct();
meta.note = 'Deterministic MATLAB fixture for dordvarx baseline/weight/noD parity checks (3 cases)';
meta.createdBy = 'testutils.generateDordvarxFixture';
meta.n_cases = n_cases;
meta.seeds = seeds;

save(outputPath, ...
    'meta', ...
    'n_cases', 'seeds', ...
    'u_c1', 'y_c1', 'f_c1', 'p_c1', ...
    'u_c2', 'y_c2', 'f_c2', 'p_c2', ...
    'u_c3', 'y_c3', 'f_c3', 'p_c3', ...
    'S_base_c1', 'X_base_c1', 'VARX_base_c1', 'U_base_c1', 'Zps_base_c1', ...
    'S_base_c2', 'X_base_c2', 'VARX_base_c2', 'U_base_c2', 'Zps_base_c2', ...
    'S_base_c3', 'X_base_c3', 'VARX_base_c3', 'U_base_c3', 'Zps_base_c3', ...
    'S_weight1_c1', 'X_weight1_c1', 'VARX_weight1_c1', 'U_weight1_c1', 'Zps_weight1_c1', ...
    'S_weight1_c2', 'X_weight1_c2', 'VARX_weight1_c2', 'U_weight1_c2', 'Zps_weight1_c2', ...
    'S_weight1_c3', 'X_weight1_c3', 'VARX_weight1_c3', 'U_weight1_c3', 'Zps_weight1_c3', ...
    'S_noD_c1', 'X_noD_c1', 'VARX_noD_c1', 'U_noD_c1', 'Zps_noD_c1', ...
    'S_noD_c2', 'X_noD_c2', 'VARX_noD_c2', 'U_noD_c2', 'Zps_noD_c2', ...
    'S_noD_c3', 'X_noD_c3', 'VARX_noD_c3', 'U_noD_c3', 'Zps_noD_c3', ...
    'u_base', 'y_base', 'f_base', 'p_base', ...
    'S_base', 'X_base', 'VARX_base', 'U_base', 'Zps_base', ...
    'S_weight1', 'X_weight1', 'VARX_weight1', 'U_weight1', 'Zps_weight1', ...
    'S_noD', 'X_noD', 'VARX_noD', 'U_noD', 'Zps_noD');

fprintf('Wrote fixture: %s\n', outputPath);
end
