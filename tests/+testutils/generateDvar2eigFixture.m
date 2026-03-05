function generateDvar2eigFixture(outputPath)
%generateDvar2eigFixture  Write MATLAB reference fixture for dvar2eig parity tests.
%
% Usage:
%   testutils.generateDvar2eigFixture
%   testutils.generateDvar2eigFixture('fixtures/matlab_reference/dvar2eig_fixture.mat')

if nargin < 1 || isempty(outputPath)
    repoRoot = fileparts(fileparts(fileparts(mfilename('fullpath'))));
    outputPath = fullfile(repoRoot, 'fixtures', 'matlab_reference', 'dvar2eig_fixture.mat');
end

outDir = fileparts(outputPath);
if ~exist(outDir, 'dir')
    mkdir(outDir);
end

n = 3;
n_cases = 3;

A_cases = zeros(n, n, n_cases);
P_cases = zeros(n^2, n^2, n_cases);
E_cases = complex(zeros(n, n_cases));
covE_cases = zeros(2 * n, 2 * n, n_cases);

A_cases(:, :, 1) = [0.84 0.10 0.00; -0.06 0.77 0.05; 0.00 0.04 0.72];
A_cases(:, :, 2) = [0.79 0.07 0.02; -0.03 0.74 0.06; 0.01 0.02 0.68];
A_cases(:, :, 3) = [0.86 0.05 0.01; -0.08 0.76 0.04; 0.00 0.03 0.71];

for i = 1:n_cases
    diagVals = linspace(1e-5, 9e-5, n^2) * (1 + 0.15 * (i - 1));
    P_cases(:, :, i) = diag(diagVals);
    [E_i, covE_i] = dvar2eig(P_cases(:, :, i), A_cases(:, :, i));
    E_cases(:, i) = E_i(:);
    covE_cases(:, :, i) = covE_i;
end

% Backward-compatible single-case aliases (case 1).
A = A_cases(:, :, 1); %#ok<NASGU>
P = P_cases(:, :, 1); %#ok<NASGU>
E = E_cases(:, 1); %#ok<NASGU>
covE = covE_cases(:, :, 1); %#ok<NASGU>

meta = struct();
meta.note = 'Deterministic MATLAB fixture for dvar2eig parity checks (3 cases)';
meta.createdBy = 'testutils.generateDvar2eigFixture';
meta.n = n;
meta.n_cases = n_cases;

save(outputPath, ...
    'meta', 'n_cases', ...
    'A_cases', 'P_cases', 'E_cases', 'covE_cases', ...
    'A', 'P', 'E', 'covE');

fprintf('Wrote fixture: %s\n', outputPath);
end
