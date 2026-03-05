function generateDmodxFixture()
%generateDmodxFixture  Generate MATLAB reference fixture for dmodx parity tests.

repoRoot = fileparts(fileparts(fileparts(mfilename('fullpath'))));
outDir = fullfile(repoRoot, 'fixtures', 'matlab_reference');
if ~exist(outDir, 'dir')
    mkdir(outDir);
end
outputPath = fullfile(outDir, 'dmodx_fixture.mat');

n_cases = 3;
seeds = [31 71 111];

for i = 1:n_cases
    rng(seeds(i), 'twister');

    rows_single = 7 + i;
    cols_single = 18 + 2 * i;
    X_single_i = randn(rows_single, cols_single);
    n_single_i = 2 + i;
    x_single_out_i = dmodx(X_single_i, n_single_i);

    X_batch_i = {
        X_single_i + 0.1 * randn(size(X_single_i)), ...
        randn(rows_single + 1, cols_single)
    };
    n_batch_i = n_single_i - 1;
    x_batch_out_i = dmodx(X_batch_i, n_batch_i);

    if i == 1
        X_single_c1 = X_single_i;
        n_single_c1 = n_single_i;
        X_single_out_c1 = x_single_out_i;
        X_batch_c1 = X_batch_i;
        n_batch_c1 = n_batch_i;
        X_batch_out_c1 = x_batch_out_i;
    elseif i == 2
        X_single_c2 = X_single_i;
        n_single_c2 = n_single_i;
        X_single_out_c2 = x_single_out_i;
        X_batch_c2 = X_batch_i;
        n_batch_c2 = n_batch_i;
        X_batch_out_c2 = x_batch_out_i;
    else
        X_single_c3 = X_single_i;
        n_single_c3 = n_single_i;
        X_single_out_c3 = x_single_out_i;
        X_batch_c3 = X_batch_i;
        n_batch_c3 = n_batch_i;
        X_batch_out_c3 = x_batch_out_i;
    end
end

meta = struct();
meta.note = 'Deterministic MATLAB fixture for dmodx parity checks (3 cases)';
meta.createdBy = 'testutils.generateDmodxFixture';
meta.n_cases = n_cases;
meta.seeds = seeds;

save(outputPath, ...
    'meta', 'n_cases', 'seeds', ...
    'X_single_c1', 'n_single_c1', 'X_single_out_c1', 'X_batch_c1', 'n_batch_c1', 'X_batch_out_c1', ...
    'X_single_c2', 'n_single_c2', 'X_single_out_c2', 'X_batch_c2', 'n_batch_c2', 'X_batch_out_c2', ...
    'X_single_c3', 'n_single_c3', 'X_single_out_c3', 'X_batch_c3', 'n_batch_c3', 'X_batch_out_c3');

fprintf('Wrote fixture: %s\n', outputPath);
end