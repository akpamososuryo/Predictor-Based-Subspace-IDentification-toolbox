function generateDvar4varxFixture(outputPath)
%generateDvar4varxFixture  Write MATLAB reference fixture for Python dvar4varx parity tests.

if nargin < 1 || isempty(outputPath)
    repoRoot = fileparts(fileparts(fileparts(mfilename('fullpath'))));
    outputPath = fullfile(repoRoot, 'fixtures', 'matlab_reference', 'dvar4varx_fixture.mat');
end

outDir = fileparts(outputPath);
if ~exist(outDir, 'dir')
    mkdir(outDir);
end

n_cases = 3;
seeds = [79 113 147];

for i = 1:n_cases
    d = testutils.makeDordvarxData('seed', seeds(i));

    [~, ~, VARX_base_i, ~, Zps_base_i] = dordvarx( ...
        d.u, d.y, d.f, d.p, 'none', 'gcv', 0, 0);
    [P_base_i, sigma_base_i] = dvar4varx(d.u, d.y, d.p, VARX_base_i, Zps_base_i);

    [~, ~, VARX_noD_i, ~, Zps_noD_i] = dordvarx( ...
        d.u, d.y, d.f, d.p, 'none', 'gcv', 0, 1);
    [P_noD_i, sigma_noD_i] = dvar4varx(d.u, d.y, d.p, VARX_noD_i, Zps_noD_i);

    if i == 1
        u_c1 = d.u;
        y_c1 = d.y;
        p_c1 = d.p;
        VARX_base_c1 = VARX_base_i;
        Zps_base_c1 = Zps_base_i;
        P_base_c1 = P_base_i;
        sigma_base_c1 = sigma_base_i;
        VARX_noD_c1 = VARX_noD_i;
        Zps_noD_c1 = Zps_noD_i;
        P_noD_c1 = P_noD_i;
        sigma_noD_c1 = sigma_noD_i;
    elseif i == 2
        u_c2 = d.u;
        y_c2 = d.y;
        p_c2 = d.p;
        VARX_base_c2 = VARX_base_i;
        Zps_base_c2 = Zps_base_i;
        P_base_c2 = P_base_i;
        sigma_base_c2 = sigma_base_i;
        VARX_noD_c2 = VARX_noD_i;
        Zps_noD_c2 = Zps_noD_i;
        P_noD_c2 = P_noD_i;
        sigma_noD_c2 = sigma_noD_i;
    else
        u_c3 = d.u;
        y_c3 = d.y;
        p_c3 = d.p;
        VARX_base_c3 = VARX_base_i;
        Zps_base_c3 = Zps_base_i;
        P_base_c3 = P_base_i;
        sigma_base_c3 = sigma_base_i;
        VARX_noD_c3 = VARX_noD_i;
        Zps_noD_c3 = Zps_noD_i;
        P_noD_c3 = P_noD_i;
        sigma_noD_c3 = sigma_noD_i;
    end
end

% Backward-compatible single-case aliases (c1).
u_base = u_c1; %#ok<NASGU>
y_base = y_c1; %#ok<NASGU>
p_base = p_c1; %#ok<NASGU>
VARX_base = VARX_base_c1; %#ok<NASGU>
Zps_base = Zps_base_c1; %#ok<NASGU>
P_base = P_base_c1; %#ok<NASGU>
sigma_base = sigma_base_c1; %#ok<NASGU>

VARX_noD = VARX_noD_c1; %#ok<NASGU>
Zps_noD = Zps_noD_c1; %#ok<NASGU>
P_noD = P_noD_c1; %#ok<NASGU>
sigma_noD = sigma_noD_c1; %#ok<NASGU>

meta = struct();
meta.note = 'Deterministic MATLAB fixture for dvar4varx base/noD parity checks (3 cases)';
meta.createdBy = 'testutils.generateDvar4varxFixture';
meta.n_cases = n_cases;
meta.seeds = seeds;

save(outputPath, ...
    'meta', ...
    'n_cases', 'seeds', ...
    'u_c1', 'y_c1', 'p_c1', ...
    'u_c2', 'y_c2', 'p_c2', ...
    'u_c3', 'y_c3', 'p_c3', ...
    'VARX_base_c1', 'Zps_base_c1', 'P_base_c1', 'sigma_base_c1', ...
    'VARX_base_c2', 'Zps_base_c2', 'P_base_c2', 'sigma_base_c2', ...
    'VARX_base_c3', 'Zps_base_c3', 'P_base_c3', 'sigma_base_c3', ...
    'VARX_noD_c1', 'Zps_noD_c1', 'P_noD_c1', 'sigma_noD_c1', ...
    'VARX_noD_c2', 'Zps_noD_c2', 'P_noD_c2', 'sigma_noD_c2', ...
    'VARX_noD_c3', 'Zps_noD_c3', 'P_noD_c3', 'sigma_noD_c3', ...
    'u_base', 'y_base', 'p_base', ...
    'VARX_base', 'Zps_base', 'P_base', 'sigma_base', ...
    'VARX_noD', 'Zps_noD', 'P_noD', 'sigma_noD');

fprintf('Wrote fixture: %s\n', outputPath);
end