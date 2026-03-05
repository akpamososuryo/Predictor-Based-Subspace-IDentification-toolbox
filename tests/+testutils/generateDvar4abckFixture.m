function generateDvar4abckFixture(outputPath)
%generateDvar4abckFixture  Write MATLAB reference fixture for Python dvar4abck parity tests.

if nargin < 1 || isempty(outputPath)
    repoRoot = fileparts(fileparts(fileparts(mfilename('fullpath'))));
    outputPath = fullfile(repoRoot, 'fixtures', 'matlab_reference', 'dvar4abck_fixture.mat');
end

outDir = fileparts(outputPath);
if ~exist(outDir, 'dir')
    mkdir(outDir);
end

n_cases = 3;
seeds_base = [83 117 151];
seeds_stable1 = [84 118 152];

for i = 1:n_cases
    d_base = testutils.makeDx2abcdkData('stable', 'seed', seeds_base(i));
    [A_base_i, B_base_i, C_base_i, K_base_i] = dx2abck( ...
        d_base.x, d_base.u, d_base.y, d_base.f, d_base.p, 'none');
    [~, ~, ~, U_base_i, Zps_base_i] = dordvarx( ...
        d_base.u, d_base.y, d_base.f, d_base.p, 'none', 'gcv', 0, 0);
    [P_base_i, sigma_base_i, dA_base_i, dB_base_i, dC_base_i, dK_base_i] = dvar4abck( ...
        d_base.x, d_base.u, d_base.y, d_base.f, d_base.p, ...
        A_base_i, B_base_i, C_base_i, K_base_i, U_base_i, Zps_base_i);

    d_stable1 = testutils.makeDx2abcdkData('unstable', 'seed', seeds_stable1(i));
    [A_stable1_i, B_stable1_i, C_stable1_i, K_stable1_i] = dx2abck( ...
        d_stable1.x, d_stable1.u, d_stable1.y, d_stable1.f, d_stable1.p, 'stable1');
    [~, ~, ~, U_stable1_i, Zps_stable1_i] = dordvarx( ...
        d_stable1.u, d_stable1.y, d_stable1.f, d_stable1.p, 'none', 'gcv', 0, 0);
    [P_stable1_i, sigma_stable1_i, dA_stable1_i, dB_stable1_i, dC_stable1_i, dK_stable1_i] = dvar4abck( ...
        d_stable1.x, d_stable1.u, d_stable1.y, d_stable1.f, d_stable1.p, ...
        A_stable1_i, B_stable1_i, C_stable1_i, K_stable1_i, U_stable1_i, Zps_stable1_i);

    if i == 1
        x_base_c1 = d_base.x;
        u_base_c1 = d_base.u;
        y_base_c1 = d_base.y;
        f_base_c1 = d_base.f;
        p_base_c1 = d_base.p;
        A_base_c1 = A_base_i;
        B_base_c1 = B_base_i;
        C_base_c1 = C_base_i;
        K_base_c1 = K_base_i;
        U_base_c1 = U_base_i;
        Zps_base_c1 = Zps_base_i;
        P_base_c1 = P_base_i;
        sigma_base_c1 = sigma_base_i;
        dA_base_c1 = dA_base_i;
        dB_base_c1 = dB_base_i;
        dC_base_c1 = dC_base_i;
        dK_base_c1 = dK_base_i;

        x_stable1_c1 = d_stable1.x;
        u_stable1_c1 = d_stable1.u;
        y_stable1_c1 = d_stable1.y;
        f_stable1_c1 = d_stable1.f;
        p_stable1_c1 = d_stable1.p;
        A_stable1_c1 = A_stable1_i;
        B_stable1_c1 = B_stable1_i;
        C_stable1_c1 = C_stable1_i;
        K_stable1_c1 = K_stable1_i;
        U_stable1_c1 = U_stable1_i;
        Zps_stable1_c1 = Zps_stable1_i;
        P_stable1_c1 = P_stable1_i;
        sigma_stable1_c1 = sigma_stable1_i;
        dA_stable1_c1 = dA_stable1_i;
        dB_stable1_c1 = dB_stable1_i;
        dC_stable1_c1 = dC_stable1_i;
        dK_stable1_c1 = dK_stable1_i;
    elseif i == 2
        x_base_c2 = d_base.x;
        u_base_c2 = d_base.u;
        y_base_c2 = d_base.y;
        f_base_c2 = d_base.f;
        p_base_c2 = d_base.p;
        A_base_c2 = A_base_i;
        B_base_c2 = B_base_i;
        C_base_c2 = C_base_i;
        K_base_c2 = K_base_i;
        U_base_c2 = U_base_i;
        Zps_base_c2 = Zps_base_i;
        P_base_c2 = P_base_i;
        sigma_base_c2 = sigma_base_i;
        dA_base_c2 = dA_base_i;
        dB_base_c2 = dB_base_i;
        dC_base_c2 = dC_base_i;
        dK_base_c2 = dK_base_i;

        x_stable1_c2 = d_stable1.x;
        u_stable1_c2 = d_stable1.u;
        y_stable1_c2 = d_stable1.y;
        f_stable1_c2 = d_stable1.f;
        p_stable1_c2 = d_stable1.p;
        A_stable1_c2 = A_stable1_i;
        B_stable1_c2 = B_stable1_i;
        C_stable1_c2 = C_stable1_i;
        K_stable1_c2 = K_stable1_i;
        U_stable1_c2 = U_stable1_i;
        Zps_stable1_c2 = Zps_stable1_i;
        P_stable1_c2 = P_stable1_i;
        sigma_stable1_c2 = sigma_stable1_i;
        dA_stable1_c2 = dA_stable1_i;
        dB_stable1_c2 = dB_stable1_i;
        dC_stable1_c2 = dC_stable1_i;
        dK_stable1_c2 = dK_stable1_i;
    else
        x_base_c3 = d_base.x;
        u_base_c3 = d_base.u;
        y_base_c3 = d_base.y;
        f_base_c3 = d_base.f;
        p_base_c3 = d_base.p;
        A_base_c3 = A_base_i;
        B_base_c3 = B_base_i;
        C_base_c3 = C_base_i;
        K_base_c3 = K_base_i;
        U_base_c3 = U_base_i;
        Zps_base_c3 = Zps_base_i;
        P_base_c3 = P_base_i;
        sigma_base_c3 = sigma_base_i;
        dA_base_c3 = dA_base_i;
        dB_base_c3 = dB_base_i;
        dC_base_c3 = dC_base_i;
        dK_base_c3 = dK_base_i;

        x_stable1_c3 = d_stable1.x;
        u_stable1_c3 = d_stable1.u;
        y_stable1_c3 = d_stable1.y;
        f_stable1_c3 = d_stable1.f;
        p_stable1_c3 = d_stable1.p;
        A_stable1_c3 = A_stable1_i;
        B_stable1_c3 = B_stable1_i;
        C_stable1_c3 = C_stable1_i;
        K_stable1_c3 = K_stable1_i;
        U_stable1_c3 = U_stable1_i;
        Zps_stable1_c3 = Zps_stable1_i;
        P_stable1_c3 = P_stable1_i;
        sigma_stable1_c3 = sigma_stable1_i;
        dA_stable1_c3 = dA_stable1_i;
        dB_stable1_c3 = dB_stable1_i;
        dC_stable1_c3 = dC_stable1_i;
        dK_stable1_c3 = dK_stable1_i;
    end
end

meta = struct();
meta.note = 'Deterministic MATLAB fixture for dvar4abck base/stable1 parity checks (3 cases)';
meta.createdBy = 'testutils.generateDvar4abckFixture';
meta.n_cases = n_cases;
meta.seeds_base = seeds_base;
meta.seeds_stable1 = seeds_stable1;

save(outputPath, ...
    'meta', ...
    'n_cases', 'seeds_base', 'seeds_stable1', ...
    'x_base_c1', 'u_base_c1', 'y_base_c1', 'f_base_c1', 'p_base_c1', ...
    'A_base_c1', 'B_base_c1', 'C_base_c1', 'K_base_c1', 'U_base_c1', 'Zps_base_c1', 'P_base_c1', 'sigma_base_c1', 'dA_base_c1', 'dB_base_c1', 'dC_base_c1', 'dK_base_c1', ...
    'x_base_c2', 'u_base_c2', 'y_base_c2', 'f_base_c2', 'p_base_c2', ...
    'A_base_c2', 'B_base_c2', 'C_base_c2', 'K_base_c2', 'U_base_c2', 'Zps_base_c2', 'P_base_c2', 'sigma_base_c2', 'dA_base_c2', 'dB_base_c2', 'dC_base_c2', 'dK_base_c2', ...
    'x_base_c3', 'u_base_c3', 'y_base_c3', 'f_base_c3', 'p_base_c3', ...
    'A_base_c3', 'B_base_c3', 'C_base_c3', 'K_base_c3', 'U_base_c3', 'Zps_base_c3', 'P_base_c3', 'sigma_base_c3', 'dA_base_c3', 'dB_base_c3', 'dC_base_c3', 'dK_base_c3', ...
    'x_stable1_c1', 'u_stable1_c1', 'y_stable1_c1', 'f_stable1_c1', 'p_stable1_c1', ...
    'A_stable1_c1', 'B_stable1_c1', 'C_stable1_c1', 'K_stable1_c1', 'U_stable1_c1', 'Zps_stable1_c1', 'P_stable1_c1', 'sigma_stable1_c1', 'dA_stable1_c1', 'dB_stable1_c1', 'dC_stable1_c1', 'dK_stable1_c1', ...
    'x_stable1_c2', 'u_stable1_c2', 'y_stable1_c2', 'f_stable1_c2', 'p_stable1_c2', ...
    'A_stable1_c2', 'B_stable1_c2', 'C_stable1_c2', 'K_stable1_c2', 'U_stable1_c2', 'Zps_stable1_c2', 'P_stable1_c2', 'sigma_stable1_c2', 'dA_stable1_c2', 'dB_stable1_c2', 'dC_stable1_c2', 'dK_stable1_c2', ...
    'x_stable1_c3', 'u_stable1_c3', 'y_stable1_c3', 'f_stable1_c3', 'p_stable1_c3', ...
    'A_stable1_c3', 'B_stable1_c3', 'C_stable1_c3', 'K_stable1_c3', 'U_stable1_c3', 'Zps_stable1_c3', 'P_stable1_c3', 'sigma_stable1_c3', 'dA_stable1_c3', 'dB_stable1_c3', 'dC_stable1_c3', 'dK_stable1_c3');

fprintf('Wrote fixture: %s\n', outputPath);
end