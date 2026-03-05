function generateDx2abcdFixture(outputPath)
%generateDx2abcdFixture  Write MATLAB reference fixture for Python dx2abcd parity tests.

if nargin < 1 || isempty(outputPath)
    repoRoot = fileparts(fileparts(fileparts(mfilename('fullpath'))));
    outputPath = fullfile(repoRoot, 'fixtures', 'matlab_reference', 'dx2abcd_fixture.mat');
end

outDir = fileparts(outputPath);
if ~exist(outDir, 'dir')
    mkdir(outDir);
end

n_cases = 3;
seeds_base = [51 151 251];
seeds_stable1 = [52 152 252];

for i = 1:n_cases
    d_base = testutils.makeDx2abcdkData('stable', 'seed', seeds_base(i));
    [A_base_i, B_base_i, C_base_i, D_base_i] = dx2abcd( ...
        d_base.x, d_base.u, d_base.y, d_base.f, d_base.p, 'none');

    d_stable1 = testutils.makeDx2abcdkData('unstable', 'seed', seeds_stable1(i));
    [A_stable1_i, B_stable1_i, C_stable1_i, D_stable1_i] = dx2abcd( ...
        d_stable1.x, d_stable1.u, d_stable1.y, d_stable1.f, d_stable1.p, 'stable1');

    if i == 1
        x_base_c1 = d_base.x;
        u_base_c1 = d_base.u;
        y_base_c1 = d_base.y;
        f_base_c1 = d_base.f;
        p_base_c1 = d_base.p;
        A_base_c1 = A_base_i;
        B_base_c1 = B_base_i;
        C_base_c1 = C_base_i;
        D_base_c1 = D_base_i;

        x_stable1_c1 = d_stable1.x;
        u_stable1_c1 = d_stable1.u;
        y_stable1_c1 = d_stable1.y;
        f_stable1_c1 = d_stable1.f;
        p_stable1_c1 = d_stable1.p;
        A_stable1_c1 = A_stable1_i;
        B_stable1_c1 = B_stable1_i;
        C_stable1_c1 = C_stable1_i;
        D_stable1_c1 = D_stable1_i;
    elseif i == 2
        x_base_c2 = d_base.x;
        u_base_c2 = d_base.u;
        y_base_c2 = d_base.y;
        f_base_c2 = d_base.f;
        p_base_c2 = d_base.p;
        A_base_c2 = A_base_i;
        B_base_c2 = B_base_i;
        C_base_c2 = C_base_i;
        D_base_c2 = D_base_i;

        x_stable1_c2 = d_stable1.x;
        u_stable1_c2 = d_stable1.u;
        y_stable1_c2 = d_stable1.y;
        f_stable1_c2 = d_stable1.f;
        p_stable1_c2 = d_stable1.p;
        A_stable1_c2 = A_stable1_i;
        B_stable1_c2 = B_stable1_i;
        C_stable1_c2 = C_stable1_i;
        D_stable1_c2 = D_stable1_i;
    else
        x_base_c3 = d_base.x;
        u_base_c3 = d_base.u;
        y_base_c3 = d_base.y;
        f_base_c3 = d_base.f;
        p_base_c3 = d_base.p;
        A_base_c3 = A_base_i;
        B_base_c3 = B_base_i;
        C_base_c3 = C_base_i;
        D_base_c3 = D_base_i;

        x_stable1_c3 = d_stable1.x;
        u_stable1_c3 = d_stable1.u;
        y_stable1_c3 = d_stable1.y;
        f_stable1_c3 = d_stable1.f;
        p_stable1_c3 = d_stable1.p;
        A_stable1_c3 = A_stable1_i;
        B_stable1_c3 = B_stable1_i;
        C_stable1_c3 = C_stable1_i;
        D_stable1_c3 = D_stable1_i;
    end
end

% Backward-compatible single-case aliases (c1).
x_base = x_base_c1; %#ok<NASGU>
u_base = u_base_c1; %#ok<NASGU>
y_base = y_base_c1; %#ok<NASGU>
f_base = f_base_c1; %#ok<NASGU>
p_base = p_base_c1; %#ok<NASGU>
A_base = A_base_c1; %#ok<NASGU>
B_base = B_base_c1; %#ok<NASGU>
C_base = C_base_c1; %#ok<NASGU>
D_base = D_base_c1; %#ok<NASGU>

x_stable1 = x_stable1_c1; %#ok<NASGU>
u_stable1 = u_stable1_c1; %#ok<NASGU>
y_stable1 = y_stable1_c1; %#ok<NASGU>
f_stable1 = f_stable1_c1; %#ok<NASGU>
p_stable1 = p_stable1_c1; %#ok<NASGU>
A_stable1 = A_stable1_c1; %#ok<NASGU>
B_stable1 = B_stable1_c1; %#ok<NASGU>
C_stable1 = C_stable1_c1; %#ok<NASGU>
D_stable1 = D_stable1_c1; %#ok<NASGU>

meta = struct();
meta.note = 'Deterministic MATLAB fixture for dx2abcd baseline and stable1 parity checks (3 cases)';
meta.createdBy = 'testutils.generateDx2abcdFixture';
meta.f = f_base_c1;
meta.p = p_base_c1;
meta.n_cases = n_cases;
meta.seeds_base = seeds_base;
meta.seeds_stable1 = seeds_stable1;

save(outputPath, ...
    'meta', ...
    'n_cases', 'seeds_base', 'seeds_stable1', ...
    'x_base_c1', 'u_base_c1', 'y_base_c1', 'f_base_c1', 'p_base_c1', 'A_base_c1', 'B_base_c1', 'C_base_c1', 'D_base_c1', ...
    'x_base_c2', 'u_base_c2', 'y_base_c2', 'f_base_c2', 'p_base_c2', 'A_base_c2', 'B_base_c2', 'C_base_c2', 'D_base_c2', ...
    'x_base_c3', 'u_base_c3', 'y_base_c3', 'f_base_c3', 'p_base_c3', 'A_base_c3', 'B_base_c3', 'C_base_c3', 'D_base_c3', ...
    'x_stable1_c1', 'u_stable1_c1', 'y_stable1_c1', 'f_stable1_c1', 'p_stable1_c1', 'A_stable1_c1', 'B_stable1_c1', 'C_stable1_c1', 'D_stable1_c1', ...
    'x_stable1_c2', 'u_stable1_c2', 'y_stable1_c2', 'f_stable1_c2', 'p_stable1_c2', 'A_stable1_c2', 'B_stable1_c2', 'C_stable1_c2', 'D_stable1_c2', ...
    'x_stable1_c3', 'u_stable1_c3', 'y_stable1_c3', 'f_stable1_c3', 'p_stable1_c3', 'A_stable1_c3', 'B_stable1_c3', 'C_stable1_c3', 'D_stable1_c3', ...
    'x_base', 'u_base', 'y_base', 'f_base', 'p_base', 'A_base', 'B_base', 'C_base', 'D_base', ...
    'x_stable1', 'u_stable1', 'y_stable1', 'f_stable1', 'p_stable1', 'A_stable1', 'B_stable1', 'C_stable1', 'D_stable1');

fprintf('Wrote fixture: %s\n', outputPath);
end