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

d = testutils.makeDordvarxData('seed', 72);

[S_base, X_base, VARX_base, U_base, Zps_base] = dordvarx( ...
    d.u, d.y, d.f, d.p, 'none', 'gcv', 0, 0);

[S_weight1, X_weight1, VARX_weight1, U_weight1, Zps_weight1] = dordvarx( ...
    d.u, d.y, d.f, d.p, 'none', 'gcv', 1, 0);

[S_noD, X_noD, VARX_noD, U_noD, Zps_noD] = dordvarx( ...
    d.u, d.y, d.f, d.p, 'none', 'gcv', 0, 1);

meta = struct();
meta.note = 'Deterministic MATLAB fixture for dordvarx baseline/weight/noD parity checks';
meta.createdBy = 'testutils.generateDordvarxFixture';

u_base = d.u; %#ok<NASGU>
y_base = d.y; %#ok<NASGU>
f_base = d.f; %#ok<NASGU>
p_base = d.p; %#ok<NASGU>

save(outputPath, ...
    'meta', ...
    'u_base', 'y_base', 'f_base', 'p_base', ...
    'S_base', 'X_base', 'VARX_base', 'U_base', 'Zps_base', ...
    'S_weight1', 'X_weight1', 'VARX_weight1', 'U_weight1', 'Zps_weight1', ...
    'S_noD', 'X_noD', 'VARX_noD', 'U_noD', 'Zps_noD');

fprintf('Wrote fixture: %s\n', outputPath);
end
