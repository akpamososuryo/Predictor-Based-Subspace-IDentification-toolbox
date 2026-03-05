function generateDordfirFixture()
%generateDordfirFixture  Generate MATLAB reference fixture for dordfir parity tests.

repoRoot = fileparts(fileparts(fileparts(mfilename('fullpath'))));
outDir = fullfile(repoRoot, 'fixtures', 'matlab_reference');
if ~exist(outDir, 'dir')
    mkdir(outDir);
end
outputPath = fullfile(outDir, 'dordfir_fixture.mat');

n_cases = 3;
seeds = [61 91 121];

for i = 1:n_cases
    d = testutils.makeDordvarxData('seed', seeds(i));

    [S_base_i, X_base_i, FIR_base_i] = dordfir(d.u, d.y, d.f, d.p, 'none', 'gcv', 0);
    [S_noD_i, X_noD_i, FIR_noD_i] = dordfir(d.u, d.y, d.f, d.p, 'none', 'gcv', 1);

    if i == 1
        u_c1 = d.u;
        y_c1 = d.y;
        f_c1 = d.f;
        p_c1 = d.p;
        S_base_c1 = S_base_i;
        X_base_c1 = X_base_i;
        FIR_base_c1 = FIR_base_i;
        S_noD_c1 = S_noD_i;
        X_noD_c1 = X_noD_i;
        FIR_noD_c1 = FIR_noD_i;
    elseif i == 2
        u_c2 = d.u;
        y_c2 = d.y;
        f_c2 = d.f;
        p_c2 = d.p;
        S_base_c2 = S_base_i;
        X_base_c2 = X_base_i;
        FIR_base_c2 = FIR_base_i;
        S_noD_c2 = S_noD_i;
        X_noD_c2 = X_noD_i;
        FIR_noD_c2 = FIR_noD_i;
    else
        u_c3 = d.u;
        y_c3 = d.y;
        f_c3 = d.f;
        p_c3 = d.p;
        S_base_c3 = S_base_i;
        X_base_c3 = X_base_i;
        FIR_base_c3 = FIR_base_i;
        S_noD_c3 = S_noD_i;
        X_noD_c3 = X_noD_i;
        FIR_noD_c3 = FIR_noD_i;
    end
end

% Backward-compatible aliases (case 1).
u_base = u_c1; %#ok<NASGU>
y_base = y_c1; %#ok<NASGU>
f_base = f_c1; %#ok<NASGU>
p_base = p_c1; %#ok<NASGU>
S_base = S_base_c1; %#ok<NASGU>
X_base = X_base_c1; %#ok<NASGU>
FIR_base = FIR_base_c1; %#ok<NASGU>
S_noD = S_noD_c1; %#ok<NASGU>
X_noD = X_noD_c1; %#ok<NASGU>
FIR_noD = FIR_noD_c1; %#ok<NASGU>

meta = struct();
meta.note = 'Deterministic MATLAB fixture for dordfir parity checks (3 cases)';
meta.createdBy = 'testutils.generateDordfirFixture';
meta.n_cases = n_cases;
meta.seeds = seeds;

save(outputPath, ...
    'meta', 'n_cases', 'seeds', ...
    'u_c1', 'y_c1', 'f_c1', 'p_c1', 'S_base_c1', 'X_base_c1', 'FIR_base_c1', 'S_noD_c1', 'X_noD_c1', 'FIR_noD_c1', ...
    'u_c2', 'y_c2', 'f_c2', 'p_c2', 'S_base_c2', 'X_base_c2', 'FIR_base_c2', 'S_noD_c2', 'X_noD_c2', 'FIR_noD_c2', ...
    'u_c3', 'y_c3', 'f_c3', 'p_c3', 'S_base_c3', 'X_base_c3', 'FIR_base_c3', 'S_noD_c3', 'X_noD_c3', 'FIR_noD_c3', ...
    'u_base', 'y_base', 'f_base', 'p_base', 'S_base', 'X_base', 'FIR_base', 'S_noD', 'X_noD', 'FIR_noD');

fprintf('Wrote fixture: %s\n', outputPath);
end
