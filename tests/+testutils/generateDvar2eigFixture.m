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
A = [0.84 0.10 0.00; -0.06 0.77 0.05; 0.00 0.04 0.72];
P = diag(linspace(1e-5, 9e-5, n^2));

[E, covE] = dvar2eig(P, A);

meta = struct();
meta.note = 'Deterministic MATLAB fixture for dvar2eig parity checks';
meta.createdBy = 'testutils.generateDvar2eigFixture';
meta.n = n;

save(outputPath, 'meta', 'A', 'P', 'E', 'covE');

fprintf('Wrote fixture: %s\n', outputPath);
end
