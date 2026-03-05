function generateDordvarmaxFixture(outputPath)
%generateDordvarmaxFixture  Write MATLAB reference fixture for dordvarmax parity tests.
%
% Usage:
%   testutils.generateDordvarmaxFixture
%   testutils.generateDordvarmaxFixture('fixtures/matlab_reference/dordvarmax_fixture.mat')

if nargin < 1 || isempty(outputPath)
    repoRoot = fileparts(fileparts(fileparts(mfilename('fullpath'))));
    outputPath = fullfile(repoRoot, 'fixtures', 'matlab_reference', 'dordvarmax_fixture.mat');
end

outDir = fileparts(outputPath);
if ~exist(outDir, 'dir')
    mkdir(outDir);
end

n_cases = 3;
seeds = [73 97 131];

for i = 1:n_cases
    d = testutils.makeDordvarxData('seed', seeds(i));
    suffix = sprintf('c%d', i);

    eval(sprintf('u_%s = d.u;', suffix));
    eval(sprintf('y_%s = d.y;', suffix));
    eval(sprintf('f_%s = d.f;', suffix));
    eval(sprintf('p_%s = d.p;', suffix));

    [S_base_i, X_base_i, VARMAX_base_i, U_base_i] = dordvarmax( ...
        d.u, d.y, d.f, d.p, 'gradient', 1e-6, 'none', 'gcv', 0, 0);
    [S_weight1_i, X_weight1_i, VARMAX_weight1_i, U_weight1_i] = dordvarmax( ...
        d.u, d.y, d.f, d.p, 'els', 1e-6, 'none', 'gcv', 1, 0);
    [S_noD_i, X_noD_i, VARMAX_noD_i, U_noD_i] = dordvarmax( ...
        d.u, d.y, d.f, d.p, 'gradient', 1e-6, 'none', 'gcv', 0, 1);

    eval(sprintf('S_base_%s = S_base_i;', suffix));
    eval(sprintf('X_base_%s = X_base_i;', suffix));
    eval(sprintf('VARMAX_base_%s = VARMAX_base_i;', suffix));
    eval(sprintf('U_base_%s = U_base_i;', suffix));

    eval(sprintf('S_weight1_%s = S_weight1_i;', suffix));
    eval(sprintf('X_weight1_%s = X_weight1_i;', suffix));
    eval(sprintf('VARMAX_weight1_%s = VARMAX_weight1_i;', suffix));
    eval(sprintf('U_weight1_%s = U_weight1_i;', suffix));

    eval(sprintf('S_noD_%s = S_noD_i;', suffix));
    eval(sprintf('X_noD_%s = X_noD_i;', suffix));
    eval(sprintf('VARMAX_noD_%s = VARMAX_noD_i;', suffix));
    eval(sprintf('U_noD_%s = U_noD_i;', suffix));
end

% Backward-compatible single-case aliases (c1).
u_base = u_c1; %#ok<NASGU>
y_base = y_c1; %#ok<NASGU>
f_base = f_c1; %#ok<NASGU>
p_base = p_c1; %#ok<NASGU>
S_base = S_base_c1; %#ok<NASGU>
X_base = X_base_c1; %#ok<NASGU>
VARMAX_base = VARMAX_base_c1; %#ok<NASGU>
U_base = U_base_c1; %#ok<NASGU>
S_weight1 = S_weight1_c1; %#ok<NASGU>
X_weight1 = X_weight1_c1; %#ok<NASGU>
VARMAX_weight1 = VARMAX_weight1_c1; %#ok<NASGU>
U_weight1 = U_weight1_c1; %#ok<NASGU>
S_noD = S_noD_c1; %#ok<NASGU>
X_noD = X_noD_c1; %#ok<NASGU>
VARMAX_noD = VARMAX_noD_c1; %#ok<NASGU>
U_noD = U_noD_c1; %#ok<NASGU>

meta = struct();
meta.note = 'Deterministic MATLAB fixture for dordvarmax baseline/weight/noD parity checks (3 cases)';
meta.createdBy = 'testutils.generateDordvarmaxFixture';
meta.n_cases = n_cases;
meta.seeds = seeds;

save(outputPath, ...
    'meta', ...
    'n_cases', 'seeds', ...
    'u_c1', 'y_c1', 'f_c1', 'p_c1', ...
    'u_c2', 'y_c2', 'f_c2', 'p_c2', ...
    'u_c3', 'y_c3', 'f_c3', 'p_c3', ...
    'S_base_c1', 'X_base_c1', 'VARMAX_base_c1', 'U_base_c1', ...
    'S_base_c2', 'X_base_c2', 'VARMAX_base_c2', 'U_base_c2', ...
    'S_base_c3', 'X_base_c3', 'VARMAX_base_c3', 'U_base_c3', ...
    'S_weight1_c1', 'X_weight1_c1', 'VARMAX_weight1_c1', 'U_weight1_c1', ...
    'S_weight1_c2', 'X_weight1_c2', 'VARMAX_weight1_c2', 'U_weight1_c2', ...
    'S_weight1_c3', 'X_weight1_c3', 'VARMAX_weight1_c3', 'U_weight1_c3', ...
    'S_noD_c1', 'X_noD_c1', 'VARMAX_noD_c1', 'U_noD_c1', ...
    'S_noD_c2', 'X_noD_c2', 'VARMAX_noD_c2', 'U_noD_c2', ...
    'S_noD_c3', 'X_noD_c3', 'VARMAX_noD_c3', 'U_noD_c3', ...
    'u_base', 'y_base', 'f_base', 'p_base', ...
    'S_base', 'X_base', 'VARMAX_base', 'U_base', ...
    'S_weight1', 'X_weight1', 'VARMAX_weight1', 'U_weight1', ...
    'S_noD', 'X_noD', 'VARMAX_noD', 'U_noD');

fprintf('Wrote fixture: %s\n', outputPath);
end
