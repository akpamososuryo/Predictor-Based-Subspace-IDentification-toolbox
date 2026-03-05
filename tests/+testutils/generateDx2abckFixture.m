function generateDx2abckFixture(outputPath)
%generateDx2abckFixture  Write MATLAB reference fixture for Python parity tests.
%
% Usage:
%   testutils.generateDx2abckFixture
%   testutils.generateDx2abckFixture('fixtures/matlab_reference/dx2abck_fixture.mat')

if nargin < 1 || isempty(outputPath)
    repoRoot = fileparts(fileparts(fileparts(mfilename('fullpath'))));
    outputPath = fullfile(repoRoot, 'fixtures', 'matlab_reference', 'dx2abck_fixture.mat');
end

outDir = fileparts(outputPath);
if ~exist(outDir, 'dir')
    mkdir(outDir);
end

d_base = testutils.makeDx2abcdkData('stable', 'seed', 51);
[A_base, B_base, C_base, K_base] = dx2abck( ...
    d_base.x, d_base.u, d_base.y, d_base.f, d_base.p, 'none');

d_stable1 = testutils.makeDx2abcdkData('unstable', 'seed', 52);
[A_stable1, B_stable1, C_stable1, K_stable1] = dx2abck( ...
    d_stable1.x, d_stable1.u, d_stable1.y, d_stable1.f, d_stable1.p, 'stable1');

meta = struct();
meta.note = 'Deterministic MATLAB fixture for dx2abck baseline and stable1 parity checks';
meta.createdBy = 'testutils.generateDx2abckFixture';
meta.f = d_base.f;
meta.p = d_base.p;

x_base = d_base.x; %#ok<NASGU>
u_base = d_base.u; %#ok<NASGU>
y_base = d_base.y; %#ok<NASGU>
f_base = d_base.f; %#ok<NASGU>
p_base = d_base.p; %#ok<NASGU>

x_stable1 = d_stable1.x; %#ok<NASGU>
u_stable1 = d_stable1.u; %#ok<NASGU>
y_stable1 = d_stable1.y; %#ok<NASGU>
f_stable1 = d_stable1.f; %#ok<NASGU>
p_stable1 = d_stable1.p; %#ok<NASGU>

save(outputPath, ...
    'meta', ...
    'x_base', 'u_base', 'y_base', 'f_base', 'p_base', 'A_base', 'B_base', 'C_base', 'K_base', ...
    'x_stable1', 'u_stable1', 'y_stable1', 'f_stable1', 'p_stable1', 'A_stable1', 'B_stable1', 'C_stable1', 'K_stable1');

fprintf('Wrote fixture: %s\n', outputPath);
end
